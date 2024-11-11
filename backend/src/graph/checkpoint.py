from contextlib import asynccontextmanager
from typing import (
    Any,
    AsyncIterator,
    Sequence,
)

from aiodynamo.client import Client, Table
from aiodynamo.credentials import Credentials
from aiodynamo.expressions import F, HashKey, RangeKey
from aiodynamo.http.aiohttp import AIOHTTP
from aiodynamo.models import KeySchema, KeySpec, KeyType, Throughput
from aiohttp import ClientSession
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    PendingWrite,
    get_checkpoint_id,
)
from langgraph.checkpoint.serde.base import SerializerProtocol
from yarl import URL

from src.core.config import settings

from .schemas import (
    CheckpointConfigurable,
    CompositeKey,
    WritesConfigurable,
    WritesData,
)

DYNAMODB_KEY_SEPARATOR = "#"


def _make_checkpoint_key(
    thread_id: str, checkpoint_ns: str, checkpoint_id: str
) -> CompositeKey:
    """Generates a composite key for a checkpoint.

    The key is formatted as follows:
        PK: "checkpoint#<thread_id>"
        SK: "<checkpoint_ns>#<checkpoint_id>"

    Args:
        thread_id (str): The thread ID of the checkpoint.
        checkpoint_ns (str): The namespace of the checkpoint.
        checkpoint_id (str): The ID of the checkpoint.

    Returns:
        CompositeKey: The composite key for the checkpoint.
    """
    return {
        "PK": DYNAMODB_KEY_SEPARATOR.join(["checkpoint", thread_id]),
        "SK": DYNAMODB_KEY_SEPARATOR.join([checkpoint_ns, checkpoint_id]),
    }


def _make_writes_key(
    thread_id: str,
    checkpoint_ns: str,
    checkpoint_id: str,
    task_id: str,
    idx: int | None,
) -> CompositeKey:
    """Generates a composite key for a writes entry.

    The key is formatted as follows:
        PK: "writes#<thread_id>"
        SK: "<checkpoint_ns>#<checkpoint_id>#<task_id>[#<idx>]"

    Args:
        thread_id (str): The thread ID of the checkpoint.
        checkpoint_ns (str): The namespace of the checkpoint.
        checkpoint_id (str): The ID of the checkpoint.
        task_id (str): The ID of the task.
        idx (int | None): The index of the write entry.

    Returns:
        CompositeKey: The composite key for the writes entry.
    """
    if idx is None:
        return {
            "PK": DYNAMODB_KEY_SEPARATOR.join(["writes", thread_id]),
            "SK": DYNAMODB_KEY_SEPARATOR.join([checkpoint_ns, checkpoint_id, task_id]),
        }

    return {
        "PK": DYNAMODB_KEY_SEPARATOR.join(["writes", thread_id]),
        "SK": DYNAMODB_KEY_SEPARATOR.join(
            [checkpoint_ns, checkpoint_id, task_id, str(idx)]
        ),
    }


def _parse_checkpoint_key(key: CompositeKey) -> CheckpointConfigurable:
    """Parses a checkpoint key into its components.

    Args:
        key (CompositeKey): The composite checkpoint key.

    Raises:
        ValueError: If the key is not a valid checkpoint key.

    Returns:
        CheckpointConfigurable: The configurable components of the checkpoint key.
    """
    namespace, thread_id = key["PK"].split(DYNAMODB_KEY_SEPARATOR)
    checkpoint_ns, checkpoint_id = key["SK"].split(DYNAMODB_KEY_SEPARATOR)

    if namespace != "checkpoint":
        raise ValueError(f"Invalid checkpoint key: {key}")

    return {
        "thread_id": thread_id,
        "checkpoint_ns": checkpoint_ns,
        "checkpoint_id": checkpoint_id,
    }


def _parse_writes_key(key: CompositeKey) -> WritesConfigurable:
    """Parses a writes key into its components.

    Args:
        key (CompositeKey): The composite writes key.

    Raises:
        ValueError: If the key is not a valid writes key.

    Returns:
        WritesConfigurable: The configurable components of the writes key.
    """
    namespace, thread_id = key["PK"].split(DYNAMODB_KEY_SEPARATOR)
    checkpoint_ns, checkpoint_id, task_id, *idx = key["SK"].split(
        DYNAMODB_KEY_SEPARATOR
    )

    if namespace != "writes":
        raise ValueError(f"Invalid writes key: {key}")

    return {
        "thread_id": thread_id,
        "checkpoint_ns": checkpoint_ns,
        "checkpoint_id": checkpoint_id,
        "task_id": task_id,
        "idx": int(idx[0]) if idx else None,
    }


def _filter_keys(
    keys: list[CompositeKey], before: RunnableConfig | None, limit: int | None
) -> list[CompositeKey]:
    """Filters a list of keys based on the before and limit parameters.

    The keys are sorted in descending order (newest first). If the before parameter is provided, only keys created before
    the specified checkpoint are returned. If the limit parameter is provided, only the first n keys are returned.

    Args:
        keys (list[CompositeKey]): The list of keys to filter.
        before (RunnableConfig | None): The configuration of the checkpoint to filter keys before.
        limit (int | None): The maximum number of keys to return.

    Returns:
        list[CompositeKey]: The filtered list of keys.
    """
    if before:
        keys = [
            key
            for key in keys
            if _parse_checkpoint_key(key)["checkpoint_id"]
            < before["configurable"]["checkpoint_id"]
        ]

    keys = sorted(
        keys, key=lambda k: _parse_checkpoint_key(k)["checkpoint_id"], reverse=True
    )
    if limit:
        keys = keys[:limit]

    return keys


def _dump_writes(
    serde: SerializerProtocol, writes: tuple[str, Any]
) -> list[WritesData]:
    """Serializes a list of writes into a list of serialized writes.

    Args:
        serde (SerializerProtocol): The serializer protocol to use.
        writes (tuple[str, Any]): The list of writes to serialize.

    Returns:
        list[WritesData]: The list of serialized writes.
    """
    serialized_writes: list[WritesData] = []
    for channel, value in writes:
        type_, serialized_value = serde.dumps_typed(value)
        serialized_writes.append(
            {"channel": channel, "type": type_, "value": serialized_value}
        )

    return serialized_writes


def _load_writes(
    serde: SerializerProtocol, task_id_to_data: dict[tuple[str, str], dict]
) -> list[PendingWrite]:
    """Deserializes a dictionary of writes into a list of pending writes.

    Args:
        serde (SerializerProtocol): The serializer protocol to use.
        task_id_to_data (dict[tuple[str, str], dict]): The dictionary of task ID to data mappings.

    Returns:
        list[PendingWrite]: The list of pending writes.
    """
    writes = [
        (
            task_id,
            data["channel"],
            serde.loads_typed(data["type"], data["value"]),
        )
        for (task_id, _), data in task_id_to_data.items()
    ]

    return writes


def _parse_checkpoint_data(
    serde: SerializerProtocol,
    key: CompositeKey,
    data: dict,
    pending_writes: list[PendingWrite] | None = None,
) -> CheckpointTuple | None:
    """Parses a checkpoint data entry into a CheckpointTuple.

    Args:
        serde (SerializerProtocol): The serializer protocol to use.
        key (CompositeKey): The composite key of the checkpoint.
        data (dict): The data of the checkpoint.
        pending_writes (list[PendingWrite] | None): The pending writes. Defaults to None.

    Returns:
        CheckpointTuple | None: The parsed checkpoint tuple, or None if the data is invalid.
    """
    if not data:
        return None

    parsed_key = _parse_checkpoint_key(key)
    thread_id = parsed_key["thread_id"]
    checkpoint_ns = parsed_key["checkpoint_ns"]
    checkpoint_id = parsed_key["checkpoint_id"]

    config = {
        "configurable": {
            "thread_id": thread_id,
            "checkpoint_ns": checkpoint_ns,
            "checkpoint_id": checkpoint_id,
        }
    }

    checkpoint = serde.loads_typed((data["type"], data["checkpoint"]))
    metadata = serde.loads(data["metadata"])
    parent_checkpoint_id = data.get("parent_checkpoint_id", "")
    parent_config = (
        {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": parent_checkpoint_id,
            }
        }
        if parent_checkpoint_id
        else None
    )

    return CheckpointTuple(
        config=config,
        checkpoint=checkpoint,
        metadata=metadata,
        parent_config=parent_config,
        pending_writes=pending_writes,
    )


class AsyncDynamoDBSaver(BaseCheckpointSaver):
    client: Client
    table: Table

    def __init__(self, client: Client, table: Table):
        super().__init__()
        self.client = client
        self.table = table

    @classmethod
    @asynccontextmanager
    async def from_conn_info(
        cls, *, region: str, table_name: str
    ) -> AsyncIterator["AsyncDynamoDBSaver"]:
        endpoint = None

        if settings.ENVIRONMENT.is_local:
            endpoint = URL.build(scheme="http", host="localhost", port=8000)

        async with ClientSession() as session:
            client = Client(
                http=AIOHTTP(session),
                credentials=Credentials.auto(),
                region=region,
                endpoint=endpoint,
            )
            table = client.table(table_name)

            if settings.ENVIRONMENT.is_local:
                if not await table.exists():
                    await table.create(
                        keys=KeySchema(
                            KeySpec("PK", KeyType.string),
                            KeySpec("SK", KeyType.string),
                        ),
                        throughput=Throughput(read=3, write=3),
                    )

            yield cls(region, table)

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        """Save a checkpoint to the database asynchronously.

        This method saves a checkpoint to DynamoDB. The checkpoint is associated
        with the provided config and its parent config (if any).

        Args:
            config (RunnableConfig): The config to associate with the checkpoint.
            checkpoint (Checkpoint): The checkpoint to save.
            metadata (CheckpointMetadata): Additional metadata to save with the checkpoint.
            new_versions (ChannelVersions): New channel versions as of this write.

        Returns:
            RunnableConfig: Updated configuration after storing the checkpoint.
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"]["checkpoint_ns"]
        checkpoint_id = checkpoint["id"]
        parent_checkpoint_id = config["configurable"].get("checkpoint_id")
        key = _make_checkpoint_key(thread_id, checkpoint_ns, checkpoint_id)

        type_, serialized_checkpoint = self.serde.dumps_typed(checkpoint)
        serialized_metadata = self.serde.dumps(metadata)
        item = {
            **key,
            "checkpoint": serialized_checkpoint,
            "type": type_,
            "checkpoint_id": checkpoint_id,
            "metadata": serialized_metadata,
            "parent_checkpoint_id": parent_checkpoint_id
            if parent_checkpoint_id
            else "",
        }

        await self.table.put_item(item)

        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
            }
        }

    async def aput_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[tuple[str, Any]],
        task_id: str,
    ) -> RunnableConfig:
        """Store intermediate writes linked to a checkpoint asynchronously.

        This method saves intermediate writes associated with a checkpoint to the database.

        Args:
            config (RunnableConfig): Configuration of the related checkpoint.
            writes (Sequence[tuple[str, Any]]): List of writes to store, each as (channel, value) pair.
            task_id (str): Identifier for the task creating the writes.

        Returns:
            RunnableConfig: Updated configuration after storing the writes.
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"]["checkpoint_ns"]
        checkpoint_id = config["configurable"]["checkpoint_id"]

        for idx, data in enumerate(_dump_writes(self.serde, writes)):
            key = _make_writes_key(
                thread_id, checkpoint_ns, checkpoint_id, task_id, idx
            )
            await self.table.put_item({**key, **data})
        return config

    async def aget_tuple(self, config: RunnableConfig) -> CheckpointTuple | None:
        """Get a checkpoint tuple from DynamoDB asynchronously.

        This method retrieves a checkpoint tuple from DynamoDB based on the
        provided config. If the config contains a "checkpoint_id" key, the checkpoint with
        the matching thread ID and checkpoint ID is retrieved. Otherwise, the latest checkpoint
        for the given thread ID is retrieved.

        Args:
            config (RunnableConfig): The config to use for retrieving the checkpoint.

        Returns:
            CheckpointTuple | None: The retrieved checkpoint tuple, or None if no matching checkpoint was found.
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = get_checkpoint_id(config)
        if not get_checkpoint_id(config):
            config = {
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": checkpoint_id,
                }
            }

        checkpoint_key = await self._aget_checkpoint_key(
            thread_id, checkpoint_ns, checkpoint_id
        )
        if not checkpoint_key:
            return None
        checkpoint_data = await self.table.get_item(checkpoint_key)

        checkpoint_id = (
            checkpoint_id or _parse_checkpoint_key(checkpoint_key)["checkpoint_id"]
        )
        writes_key = _make_writes_key(thread_id, checkpoint_ns, checkpoint_id, "", None)
        matching_keys = [
            key
            async for key in self.table.query(
                key_condition=HashKey("PK", writes_key["PK"])
                & RangeKey("SK").begins_with(writes_key["SK"]),
                projection=F("PK") & F("SK"),
            )
        ]
        parsed_keys = [_parse_writes_key(key) for key in matching_keys]
        pending_writes = _load_writes(
            self.serde,
            {
                (parsed_keys["task_id"], parsed_keys["idx"]): await self.table.get_item(
                    key
                )
                for key, parsed_keys in sorted(
                    zip(matching_keys, parsed_keys), key=lambda x: x[1]["idx"]
                )
            },
        )
        return _parse_checkpoint_data(
            self.serde, checkpoint_key, checkpoint_data, pending_writes
        )

    async def alist(
        self,
        config: RunnableConfig | None,
        *,
        # TODO: Implement filtering
        filter: dict[str, Any] | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[CheckpointTuple]:
        """List checkpoints from DynamoDB asynchronously.

        This method retrieves a list of checkpoint tuples from DynamoDB based
        on the provided config. The checkpoints are ordered by checkpoint ID in descending order (newest first).

        Args:
            config (RunnableConfig | None): Base configuration for filtering checkpoints.
            filter (dict[str, Any] | None): Additional filtering criteria for metadata. Defaults to None.
            before (RunnableConfig | None): If provided, only checkpoints before the specified checkpoint ID are returned. Defaults to None.
            limit (int | None): Maximum number of checkpoints to return. Defaults to None.

        Yields:
            AsyncIterator[CheckpointTuple]: An asynchronous iterator of matching checkpoint tuples.
        """
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        key = _make_checkpoint_key(thread_id, checkpoint_ns, "")
        matching_keys = _filter_keys(
            [
                key
                async for key in self.table.query(
                    key_condition=HashKey("PK", key["PK"])
                    & RangeKey("SK").begins_with(key["SK"]),
                    projection=F("PK") & F("SK"),
                )
            ],
            before,
            limit,
        )
        for key in matching_keys:
            data = await self.table.get_item(key)
            if data and "checkpoint" in data and "metadata" in data:
                yield _parse_checkpoint_data(self.serde, key, data)

    async def _aget_checkpoint_key(
        self, thread_id: str, checkpoint_ns: str, checkpoint_id: str | None
    ) -> CompositeKey | None:
        """Determines the latest checkpoint key

        Args:
            thread_id (str): The thread ID of the checkpoint.
            checkpoint_ns (str): The namespace of the checkpoint.
            checkpoint_id (str | None): The ID of the checkpoint

        Returns:
            CompositeKey | None: The latest checkpoint key.
        """
        if checkpoint_id:
            return _make_checkpoint_key(thread_id, checkpoint_ns, checkpoint_id)

        all_keys = [
            key
            async for key in self.table.query(
                key_condition=HashKey("PK", f"checkpoint#{thread_id}")
                & RangeKey("SK").begins_with(
                    DYNAMODB_KEY_SEPARATOR.join([checkpoint_ns, ""])
                ),
                projection=F("PK") & F("SK"),
            )
        ]

        if not all_keys:
            return None

        latest_key = max(
            all_keys, key=lambda k: _parse_checkpoint_key(k)["checkpoint_id"]
        )

        return latest_key

from functools import lru_cache
from pathlib import Path
from chromadb import Collection, PersistentClient, errors as chromadb_errors
from chromadb.utils import embedding_functions
from typing import Optional

from src.core.logging import Logger
from src.core.config import settings

logger = Logger(__name__).logger


class ChromaDB:
    def __init__(
        self,
        persistent_path: str = str(Path.home() / "titan-vectorstore"),
        embedding_model: str = "text-embedding-3-small",
    ):
        self._client: Optional[PersistentClient] = None
        self._persistent_path = persistent_path
        self._embedding_model = embedding_model
        self._collections: dict[str, Collection] = {}

    def initialize(self) -> None:
        """Initialize the ChromaDB client and default collections."""
        if not self._client:
            self._client = PersistentClient(path=self._persistent_path)
            self._setup_collections()

    def _setup_collections(self) -> None:
        """Set up default collections with embeddings configuration."""
        embedder = embedding_functions.OpenAIEmbeddingFunction(
            model_name=self._embedding_model,
            api_key=settings.OPENAI_API_KEY,
        )

        try:
            collection = None
            try:
                collection = self._client.get_collection("document")
            except chromadb_errors.InvalidCollectionException:
                collection = self._client.create_collection(
                    name="document",
                    embedding_function=embedder,
                )
                logger.info(
                    f"ChromaDB: Document collection initialized at {self._persistent_path}"
                )

            self._collections["document"] = collection
            if collection:
                logger.info(
                    f"ChromaDB: Document collection successfully loaded at {self._persistent_path}"
                )
        except Exception as e:
            logger.error(f"ChromaDB: Error initializing document collection: {e}")
            raise

    @property
    def document_collection(self) -> Collection:
        """Get the document collection."""
        if not self._client:
            raise RuntimeError(
                "ChromaDB has not been initialized. Call initialize() first."
            )
        return self._collections["document"]


@lru_cache
def get_chroma_db() -> ChromaDB:
    """Get the ChromaDB instance."""
    return ChromaDB()

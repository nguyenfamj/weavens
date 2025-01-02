from .db import get_db
from ..common.constants import Database
from langchain_core.messages import HumanMessage
import uuid
from datetime import datetime

user_message_logs_table = get_db().resource.Table(Database.USER_MESSAGE_LOGS_TABLE_NAME)


def log_user_message(message: HumanMessage) -> None:
    user_message_logs_table.put_item(
        Item={
            "id": str(uuid.uuid4()),
            "message": message.content,
            "created_at": datetime.now().isoformat(),
        }
    )

import json
from datetime import datetime
from uuid import uuid4

from airflow import DAG
from airflow.models.taskinstance import TaskInstance
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.dynamodb import DynamoDBHook
from boto3.dynamodb.conditions import Attr, Key

default_args = {
    "owner": "thangphan",
    "email": "thangphan.dev@gmail.com",
}


def prepare_batch_file():
    db = DynamoDBHook(aws_conn_id="aws_default", table_name="OikotieProperties")

    connection = db.get_conn()

    table = connection.Table(db.table_name)

    items = table.query(
        IndexName="GSI2",
        KeyConditionExpression=(Key("translated").eq(0)),
        FilterExpression=(
            Attr("completed_renovations").exists() | Attr("future_renovations").exists()
        ),
        ProjectionExpression="oikotie_id,completed_renovations,future_renovations",
    )["Items"]

    input_file_id = str(uuid4())[:8]
    input_file = f"/tmp/file_{input_file_id}_input.jsonl"

    with open(input_file, "w") as f:
        for item in items:
            item["oikotie_id"] = int(item["oikotie_id"])
            request = {
                "custom_id": str(item["oikotie_id"]),
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": 'Translate the following text from Finnish to English then summarize. Format the output as follows: {"completed_renovations": <translated completed renovations>, "future_renovations": <translated future renovations>}',
                        },
                        {
                            "role": "user",
                            "content": f"Completed renovations: {item.get("completed_renovations")}, Future renovations: {item.get("future_renovations")}",
                        },
                    ],
                },
            }
            json.dump(request, f)
            f.write("\n")

    return input_file


def upload_file(ti: TaskInstance):
    from openai import OpenAI

    client = OpenAI()

    input_file = ti.xcom_pull(task_ids="prepare_batch_file")

    batch_input_file = client.files.create(file=open(input_file, "rb"), purpose="batch")

    return dict(batch_input_file)


def create_batch(ti: TaskInstance):
    from openai import OpenAI

    client = OpenAI()

    batch_input_file = ti.xcom_pull(task_ids="upload_file")
    batch_input_file_id = batch_input_file.get("id")

    created_batch = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )

    created_batch_dict = dict(created_batch)
    created_batch_dict["request_counts"] = {
        "total": created_batch.request_counts.total,
        "completed": created_batch.request_counts.completed,
        "failed": created_batch.request_counts.failed,
    }

    return created_batch_dict


with DAG(
    dag_id="create_translation_batch",
    schedule_interval="0 5 * * *",
    start_date=datetime(2024, 8, 8),
    catchup=False,
    default_args=default_args,
) as dag:
    task1 = PythonOperator(
        task_id="prepare_batch_file",
        python_callable=prepare_batch_file,
    )

    task2 = PythonOperator(
        task_id="upload_file",
        python_callable=upload_file,
    )

    task3 = PythonOperator(
        task_id="create_batch",
        python_callable=create_batch,
    )

    task1 >> task2 >> task3

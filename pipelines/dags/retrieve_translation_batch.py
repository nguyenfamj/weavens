import json
import logging
import time
from datetime import datetime

from airflow import DAG
from airflow.models.taskinstance import TaskInstance
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.dynamodb import DynamoDBHook
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

default_args = {
    "owner": "thangphan",
    "email": "thangphan.dev@gmail.com",
}


def check_batch_status(ti: TaskInstance):
    from openai import OpenAI

    client = OpenAI()

    batch = ti.xcom_pull(
        task_ids="create_batch",
        dag_id="create_translation_batch",
        include_prior_dates=True,
    )
    batch_id = batch.get("id")

    while True:
        batch = client.batches.retrieve(batch_id)
        batch_status = batch.status

        if batch_status == "completed":
            batch_dict = dict(batch)
            batch_dict["request_counts"] = {
                "total": batch.request_counts.total,
                "completed": batch.request_counts.completed,
                "failed": batch.request_counts.failed,
            }
            return batch_dict
        elif batch_status == "failed":
            raise Exception(f"Batch with ID {batch_id} failed.")
        elif batch_status == "expired":
            raise Exception(f"Batch with ID {batch_id} expired.")
        elif batch_status in ["cancelled", "cancelling"]:
            raise Exception(f"Batch with ID {batch_id} was cancelled.")

        time.sleep(30)


def get_batch_results(ti: TaskInstance):
    from openai import OpenAI

    client = OpenAI()
    batch = ti.xcom_pull(task_ids="check_batch_status")
    output_file_id = batch.get("output_file_id")
    output_file = client.files.content(output_file_id)

    output_file_path = f"/tmp/{output_file_id}.jsonl"
    with open(output_file_path, "w") as f:
        f.write(output_file.text)

    return output_file_path


def write_to_dynamodb(ti: TaskInstance):
    db = DynamoDBHook(aws_conn_id="aws_default", table_name="OikotieProperties")
    connection = db.get_conn()
    table = connection.Table(db.table_name)

    output_file_path = ti.xcom_pull(task_ids="get_batch_results")
    with open(output_file_path, "r") as f:
        for line in f:
            response = json.loads(line)
            item = {}
            if response["response"]["status_code"] == 200:
                item["id"] = int(response["custom_id"])
                try:
                    content_dict = json.loads(
                        response["response"]["body"]["choices"][0]["message"]["content"]
                    )
                    for key in ["completed_renovations", "future_renovations"]:
                        item[f"{key}_EN"] = content_dict[key]
                        if isinstance(item[f"{key}_EN"], list):
                            item[f"{key}_EN"] = "\n".join(item[f"{key}_EN"])

                except Exception as e:
                    print(f"Error parsing response of {item["id"]}", e)

                try:
                    response = table.update_item(
                        Key={"id": item["id"]},
                        UpdateExpression="SET completed_renovations_EN = :cr, future_renovations_EN = :fr, translated = :t",
                        ExpressionAttributeValues={
                            ":cr": item["completed_renovations_EN"],
                            ":fr": item["future_renovations_EN"],
                            ":t": 1,
                        },
                    )
                except ClientError as err:
                    logger.error(
                        "Could not update item with id %s in table %s. Error code: %s. Error message: %s",
                        item["id"],
                        table.name,
                        err.response["Error"]["Code"],
                        err.response["Error"]["Message"],
                    )
                    raise


with DAG(
    dag_id="retrieve_translation_batch",
    schedule_interval="0 5 * * *",
    start_date=datetime(2024, 8, 8),
    catchup=False,
    default_args=default_args,
) as dag:
    task1 = PythonOperator(
        task_id="check_batch_status",
        python_callable=check_batch_status,
    )

    task2 = PythonOperator(
        task_id="get_batch_results",
        python_callable=get_batch_results,
    )

    task3 = PythonOperator(
        task_id="write_to_dynamodb",
        python_callable=write_to_dynamodb,
    )

    task1 >> task2 >> task3

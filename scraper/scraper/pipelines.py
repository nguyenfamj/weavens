# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os
import re

import boto3
from botocore.exceptions import ClientError
from itemadapter import ItemAdapter
from scrapy import Spider
from scrapy.exceptions import DropItem

from .db import DynamoDB


class DuplicateFilterPipeline:
    def __init__(self, table_name):
        self.table_name = table_name
        self.db = DynamoDB(table_name=self.table_name)

    @classmethod
    def from_crawler(cls, crawler):
        table_name = crawler.settings.get("PROPERTY_TABLE_NAME")
        return cls(table_name=table_name)

    def process_item(self, item, spider: Spider):
        adapter = ItemAdapter(item)
        if spider.name == "oikotie_url":
            id = adapter.get("id")
            if self.db.table.get_item(Key={"id": id}).get("Item"):
                raise DropItem()

        return item


class ExtractNumberOfBedroomsPipeline:
    def process_item(self, item, spider: Spider):
        adapter = ItemAdapter(item)
        number_of_rooms = adapter.get("number_of_rooms")
        if number_of_rooms and number_of_rooms > 0:
            if number_of_rooms > 1:
                item["number_of_bedrooms"] = number_of_rooms - 1
            else:
                item["number_of_bedrooms"] = 1

        return item


class PutToDynamoDBPipeline:
    def __init__(self, table_name):
        self.table_name = table_name
        self.db = DynamoDB(table_name=self.table_name)

    @classmethod
    def from_crawler(cls, crawler):
        table_name = crawler.settings.get("PROPERTY_TABLE_NAME")
        return cls(table_name=table_name)

    def open_spider(self, spider: Spider):
        pass

    def close_spider(self, spider: Spider):
        pass

    def process_item(self, item, spider: Spider):
        processed_item = {k: v for k, v in ItemAdapter(item).asdict().items()}
        if spider.name == "oikotie_url":
            processed_item.update({"translated": 0, "crawled": 0})
            self.db.table.put_item(Item=processed_item)
        if spider.name == "oikotie":
            processed_item.update({"translated": 0, "crawled": 1})
            self.db.table.put_item(Item=processed_item)

        return item


class PutToDynamoDBBatchPipeline:
    def __init__(self, scraped_content_table_name, scraped_content_batch_size):
        self.scraped_content_table_name = scraped_content_table_name
        self.scraped_content_batch_size = scraped_content_batch_size
        self.url_in_batch = set()
        self.scraped_content_items = []

    @classmethod
    def from_crawler(cls, crawler):
        scraped_content_table_name = crawler.settings.get("SCRAPED_CONTENT_TABLE_NAME")
        scraped_content_batch_size = crawler.settings.get("SCRAPED_CONTENT_BATCH_SIZE")
        return cls(
            scraped_content_table_name=scraped_content_table_name,
            scraped_content_batch_size=scraped_content_batch_size,
        )

    def open_spider(self, spider: Spider):
        self.scraped_content_table_session = DynamoDB(
            table_name=self.scraped_content_table_name
        )

    def close_spider(self, spider: Spider):
        self.batch_write_scraped_content()

    def process_item(self, item, spider: Spider):
        if (
            spider.name == "personalfinance_fi_url"
            or spider.name == "maanmittauslaitos_url"
            or spider.name == "expat_finland_url"
        ):
            if (
                not self.scraped_content_table_session.is_item_exists(
                    hash_key_value={"url": item["url"]}
                )
                and item["url"] not in self.url_in_batch
            ):
                self.scraped_content_items.append(dict(item))
                self.url_in_batch.add(item["url"])
            else:
                print(f"Item already exists in DynamoDB: {item['url']}")

            # Safe mechanism in case the list has more items than the batch size
            if len(self.scraped_content_items) >= self.scraped_content_batch_size:
                self.batch_write_scraped_content()

    def batch_write_scraped_content(self):
        if not self.scraped_content_items:
            return
        try:
            with self.scraped_content_table_session.table.batch_writer() as batch:
                print(f"Writing {len(self.scraped_content_items)} items to DynamoDB")

                for item in self.scraped_content_items:
                    batch.put_item(Item=item)

            # Reset batch
            self.scraped_content_items = []
            self.url_in_batch = set()
        except ClientError as e:
            raise DropItem(f"Failed to write items to DynamoDB: {str(e)}")


class PutToS3Pipeline:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    @classmethod
    def from_crawler(cls, crawler):
        bucket_name = crawler.settings.get("S3_BUCKET")

        return cls(bucket_name=bucket_name)

    def process_item(self, item, spider: Spider):
        if spider.name == "personalfinance_fi":
            if not item["url"]:
                raise DropItem(f"No URL in item (Spider: {spider.name})")
            # Extract the desired part from the URL using regex
            url_pattern = r"https?://(?:www\.)?(.+?)/?$"
            match = re.search(url_pattern, item["url"])

            object_key = None
            if match:
                object_key = f"{match.group(1)}.json"
            else:
                object_key = f"{item['url']}.json"

            json_data = json.dumps(item, ensure_ascii=False, indent=4)

            # Check if the environment is production
            if os.environ.get("ENVIRONMENT") == "PRODUCTION":
                # S3 client
                s3_client = boto3.client("s3")

                try:
                    print(
                        f"Uploading item {object_key} to S3 bucket: {self.bucket_name}"
                    )
                    s3_client.put_object(
                        Bucket=self.bucket_name,
                        Key=object_key,
                        Body=json_data.encode("utf-8"),
                        ContentType="application/json",
                    )
                    print(f"Uploaded item to S3: {object_key}")
                except Exception as e:
                    print(f"Error uploading item to S3: {e}")
            elif (
                os.environ.get("ENVIRONMENT") == "LOCAL"
                and self.bucket_name == "local-storage"
            ):
                print(f"Saving item to local storage: {object_key}")
                file_path = os.path.join(".data", object_key)
                # Ensure the directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w") as f:
                    f.write(json_data)
                print(f"Saved item to file system: {file_path}")
            else:
                print(
                    "Not in development or production, skipping saving to S3 or local storage"
                )

        return item

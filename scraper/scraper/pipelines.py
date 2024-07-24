# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import boto3
from itemadapter import ItemAdapter

from .utils import TextUtils


class ExtractPricePipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        fields = ["price_no_tax", "sales_price", "condominium_payment"]
        for field in fields:
            if adapter.get(field):
                adapter[field] = TextUtils.extract_price(adapter[field])

        return item


class ExtractAreaPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        fields = ["life_sq"]
        for field in fields:
            if adapter.get(field):
                adapter[field] = TextUtils.extract_area(adapter[field])

        return item


class ExtractCastToIntPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        fields = ["oikotie_id", "build_year"]
        for field in fields:
            if adapter.get(field):
                adapter[field] = TextUtils.cast_to_int(adapter[field])

        return item


class DynamoDBPipeline:
    def __init__(self, table_name, endpoint_url):
        self.table_name = table_name
        self.endpoint_url = endpoint_url
        self.table = None

    @classmethod
    def from_crawler(cls, crawler):
        table_name = crawler.settings.get("DYNAMODB_TABLE_NAME")
        endpoint_url = crawler.settings.get("DYNAMODB_ENDPOINT_URL")
        return cls(table_name=table_name, endpoint_url=endpoint_url)

    def open_spider(self, spider):
        db = boto3.resource("dynamodb", endpoint_url=self.endpoint_url)
        self.table = db.Table(self.table_name)

    def close_spider(self, spider):
        self.table = None

    def process_item(self, item, spider):
        self.table.put_item(
            Item={k: v for k, v in ItemAdapter(item).asdict().items() if v}
        )
        return item

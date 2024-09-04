# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from itemadapter import ItemAdapter
from scrapy import Spider
from scrapy.exceptions import DropItem

from .constants import (
    BUILDING_TYPE_TRANSLATIONS,
    HOUSING_TYPE_TRANSLATIONS,
    PROPERTY_OWNERSHIP_TRANSLATIONS,
)
from .db import DynamoDB


class ExtractFloorNumberPipeline:
    def process_item(self, item, spider: Spider):
        if spider.name == "oikotie":
            adapter = ItemAdapter(item)
            field = "floor"
            if adapter.get(field) and isinstance(adapter[field], str):
                try:
                    adapter[field] = int(adapter[field].split("/")[0])
                except ValueError:
                    pass

        return item


class ExtractCastToBoolPipeline:
    def process_item(self, item, spider: Spider):
        if spider.name == "oikotie":
            adapter = ItemAdapter(item)
            fields = ["building_has_elevator", "building_has_sauna", "has_balcony"]
            for field in fields:
                if adapter.get(field):
                    adapter[field] = TextUtils.cast_to_bool(adapter[field])

        return item


class ExtractFloorNumberPipeline:
    def process_item(self, item, spider: Spider):
        if spider.name == "oikotie":
            adapter = ItemAdapter(item)
            field = "floor"
            if adapter.get(field) and isinstance(adapter[field], str):
                try:
                    adapter[field] = int(adapter[field].split("/")[0])
                except ValueError:
                    pass

        return item


class TranslationPipeline:
    def process_item(self, item, spider: Spider):
        if spider.name == "oikotie":
            adapter = ItemAdapter(item)
            field_translation_dict = {
                "property_ownership": PROPERTY_OWNERSHIP_TRANSLATIONS,
                "housing_type": HOUSING_TYPE_TRANSLATIONS,
                "building_type": BUILDING_TYPE_TRANSLATIONS,
            }
            for field in field_translation_dict.keys():
                value = adapter.get(field)
                if value:
                    value = str(value).lower()
                    adapter[field] = field_translation_dict[field][value]

        return item


class DuplicateFilterPipeline:
    def __init__(self, table_name, endpoint_url):
        self.table_name = table_name
        self.endpoint_url = endpoint_url
        self.db = DynamoDB(table_name=self.table_name, endpoint_url=self.endpoint_url)

    @classmethod
    def from_crawler(cls, crawler):
        table_name = crawler.settings.get("DYNAMODB_TABLE_NAME")
        endpoint_url = crawler.settings.get("DYNAMODB_ENDPOINT_URL")
        return cls(table_name=table_name, endpoint_url=endpoint_url)

    def process_item(self, item, spider: Spider):
        adapter = ItemAdapter(item)
        if spider.name == "oikotie_url":
            id = adapter.get("id")
            if self.db.table.get_item(Key={"id": id}).get("Item"):
                raise DropItem()

        return item


class PutToDynamoDBPipeline:
    def __init__(self, table_name, endpoint_url):
        self.table_name = table_name
        self.endpoint_url = endpoint_url
        self.db = DynamoDB(table_name=self.table_name, endpoint_url=self.endpoint_url)

    @classmethod
    def from_crawler(cls, crawler):
        table_name = crawler.settings.get("DYNAMODB_TABLE_NAME")
        endpoint_url = crawler.settings.get("DYNAMODB_ENDPOINT_URL")
        return cls(table_name=table_name, endpoint_url=endpoint_url)

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

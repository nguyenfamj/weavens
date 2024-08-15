import json
from typing import Any

from boto3.dynamodb.conditions import Key
from redis import from_url
from scrapy.http import Response
from scrapy.loader import ItemLoader
from scrapy_redis.spiders import RedisSpider

from ..constants import TITLE_TO_FIELD
from ..db import DynamoDB
from ..items import OikotieItem
from ..settings import DYNAMODB_ENDPOINT_URL, DYNAMODB_TABLE_NAME, REDIS_URL


class OikotieSpider(RedisSpider):
    name = "oikotie"
    allowed_domains = ["asunnot.oikotie.fi"]
    limit = 24

    # Redis config
    redis_key = "scraper:start_urls"
    redis_batch_size = 12
    max_idle_time = 7  # seconds

    title_to_field = TITLE_TO_FIELD

    def __init__(self, name: str | None = name, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.add_url_to_redis_client()

    def parse(self, response: Response):
        url = response.url
        id = url.split("/")[-1]

        il = ItemLoader(item=OikotieItem(), response=response)
        il.add_value("url", url)
        il.add_value("id", id)

        # Extract data from table
        table_xpath = '//dt[text()="{title}"]/following-sibling::dd[1]//text()'
        for title, field in self.title_to_field.items():
            il.add_xpath(field, table_xpath.format(title=title))

        return il.load_item()

    def add_url_to_redis_client(self):
        redis_client = from_url(REDIS_URL)

        db = DynamoDB(
            table_name=DYNAMODB_TABLE_NAME,
            endpoint_url=DYNAMODB_ENDPOINT_URL,
        )

        items = db.table.query(
            IndexName="GSI3",
            KeyConditionExpression=(Key("crawled").eq(0)),
        ).get("Items", [])

        if not items:
            raise ValueError("No items need to be crawled")

        for item in items[: self.limit]:
            redis_client.lpush(self.redis_key, json.dumps({"url": item["url"]}))

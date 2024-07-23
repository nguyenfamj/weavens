from scrapy.http import Response
from scrapy.loader import ItemLoader
from scrapy_redis.spiders import RedisSpider

from ..constants import TITLE_TO_FIELD
from ..items import OikotieItem


class OikotieSpider(RedisSpider):
    name = "oikotie"
    allowed_domains = ["asunnot.oikotie.fi"]

    # Redis config
    redis_key = "scraper:start_urls"
    redis_batch_size = 10
    max_idle_time = 7  # seconds

    title_to_field = TITLE_TO_FIELD

    def parse(self, response: Response):
        il = ItemLoader(item=OikotieItem(), response=response)
        il.add_value("url", response.url)

        # Extract data from table
        table_xpath = '//dt[text()="{title}"]/following-sibling::dd[1]//text()'
        for title, field in self.title_to_field.items():
            il.add_xpath(field, table_xpath.format(title=title))

        return il.load_item()

from scrapy import Request, Spider
from scrapy.http import Response
from scrapy_playwright.page import PageMethod
from urllib.parse import quote
import json
import logging

from ..items import OikotieItem, OikotieItemLoader


logger = logging.getLogger(__name__)


def build_url(
    pagination: int,
    locations: list[list[int, int, str]],
    building_types: list[int],
    room_counts: list[int],
    habitation_types: list[int],
):
    json_locations = json.dumps(locations)
    # Build building types string
    building_types_str = "&".join(
        [f"{quote('buildingType[]')}={bt}" for bt in building_types]
    )

    # Build room counts string
    room_counts_str = "&".join([f"{quote('roomCount[]')}={rc}" for rc in room_counts])

    # Build habitation types string
    habitation_types_str = "&".join(
        [f"{quote('habitationType[]')}={ht}" for ht in habitation_types]
    )

    # Hardcoded values for Uusimaa region
    url = (
        f"https://asunnot.oikotie.fi/myytavat-uudisasunnot/uusimaa/kerrostalo"
        f"?pagination={pagination}"
        f"&locations={quote(json_locations)}"
        f"&{building_types_str}"
        f"&{room_counts_str}"
        f"&{habitation_types_str}"
    )

    return url


class OikotieUrlSpider(Spider):
    name = "oikotie_url"
    custom_settings = dict(
        DOWNLOAD_HANDLERS={
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        DOWNLOAD_DELAY=5,
        CONCURRENT_REQUESTS_PER_DOMAIN=2,
    )

    def __init__(self, start_page=None, end_page=None, *args, **kwargs):
        super(OikotieUrlSpider, self).__init__(*args, **kwargs)
        self.start_page = int(start_page) if start_page is not None else 1
        self.end_page = int(end_page) if end_page is not None else 20

    def start_requests(self):
        locations = [[39, 6, "Espoo"], [64, 6, "Helsinki"], [65, 6, "Vantaa"]]
        building_types = [1, 256]
        room_counts = [1, 2]
        habitation_types = [1]

        for i in range(self.start_page, self.end_page):
            url = build_url(i, locations, building_types, room_counts, habitation_types)
            logger.info(f"Scraping page {url}, page {i}/{self.end_page}")

            yield Request(
                url,
                meta=dict(
                    playwright=True,
                    playwright_include_page=True,
                    playwright_page_methods=[
                        PageMethod("wait_for_timeout", 10000),
                    ],
                ),
            )

    async def parse(self, response: Response):
        page = response.meta["playwright_page"]

        await page.close()

        for link in response.css("a.ot-card-v2"):
            il = OikotieItemLoader(item=OikotieItem(), selector=link)
            il.add_css("url", "::attr(href)")
            il.add_css("id", "::attr(analytics-click-card-id)")

            yield il.load_item()

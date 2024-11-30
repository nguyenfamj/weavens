from scrapy import Request, Spider
from scrapy.http import Response
from scrapy_playwright.page import PageMethod
from urllib.parse import quote
import json

from ..items import OikotieItem, OikotieItemLoader


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
        DOWNLOAD_DELAY=10,
    )

    def start_requests(self):
        locations = [[39, 6, "Espoo"], [64, 6, "Helsinki"], [65, 6, "Vantaa"]]
        building_types = [1, 256]
        room_counts = [1, 2]
        habitation_types = [1]

        start_page = 1 if self.start_page is None else self.start_page
        end_page = 20 if self.end_page is None else self.end_page
        
        for i in range(start_page, end_page):
            url = build_url(i, locations, building_types, room_counts, habitation_types)

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

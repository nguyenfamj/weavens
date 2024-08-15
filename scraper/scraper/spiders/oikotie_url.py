from scrapy import Request, Spider
from scrapy.http import Response
from scrapy_playwright.page import PageMethod

from ..items import OikotieItem


class OikotieUrlSpider(Spider):
    name = "oikotie_url"

    def start_requests(self):
        # TODO: Change the range to the desired number of pages
        for i in range(1, 10):
            url = f"https://asunnot.oikotie.fi/myytavat-asunnot?pagination={i}"

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
            il = ItemLoader(item=OikotieItem(), selector=link)
            il.add_css("url", "::attr(href)")
            il.add_css("id", "::attr(analytics-click-card-id)")
            yield il.load_item()

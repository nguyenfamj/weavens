from scrapy.spiders import SitemapSpider
from scraper.utils import ScraperUtils
from scraper.items import ScrapeContentItem
import re


class ExpatFinlandUrlSpider(SitemapSpider):
    name = "expat_finland_url"
    sitemap_urls = [
        "https://www.expat-finland.com/sitemap.xml",
    ]
    sitemap_rules = [(re.compile(r"/(housing|finance)/"), "parse")]

    def parse(self, response):
        # Extract all URLs from the page
        important_urls = ScraperUtils.extract_important_urls_from_response(response)

        for url in important_urls:
            yield ScrapeContentItem(
                url=url["url"],
                type=url["type"],
                mime_type=url["mime_type"],
                source_page=response.url,
                status="NOT_SCRAPED",
            )

        yield ScrapeContentItem(
            url=response.url,
            type="web_document",
            status="NOT_SCRAPED",
        )

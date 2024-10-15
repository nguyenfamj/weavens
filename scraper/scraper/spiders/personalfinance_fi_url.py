from scrapy.spiders import SitemapSpider
from scraper.utils import ScraperUtils
from scraper.items import ScrapeContentItem


class PersonalFinanceFIURLSpider(SitemapSpider):
    name = "personalfinance_fi_url"
    sitemap_urls = [
        "https://www.personalfinance.fi/sitemap_index.xml",
    ]
    sitemap_follow = ["post-sitemap\\.xml$"]

    def parse(self, response):
        # Extract all URLs from the page
        important_urls = ScraperUtils.extract_important_urls_from_response(response)

        for url in important_urls:
            yield ScrapeContentItem(
                url=url["url"],
                type=url["type"],
                mime_type=url["mime_type"],
                source_page=response.url,
            )

        yield ScrapeContentItem(
            url=response.url,
            type="web_document",
        )

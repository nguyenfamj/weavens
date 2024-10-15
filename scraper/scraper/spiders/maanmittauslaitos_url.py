from scrapy.spiders import SitemapSpider
from scraper.utils import ScraperUtils
from scraper.items import ScrapeContentItem
import re


class MaanmittauslaitosURLSpider(SitemapSpider):
    name = "maanmittauslaitos_url"
    sitemap_urls = [
        "https://www.maanmittauslaitos.fi/sitemap.xml",
    ]
    sitemap_rules = [
        (re.compile(r"/en/(real-property|apartments)/"), "parse_english_page")
    ]

    def sitemap_filter(self, entries):
        for entry in entries:
            # Check if this is a sitemap index entry
            if "loc" in entry and "sitemap.xml" in entry["loc"]:
                # If it's a sitemap index entry, yield it to process the child sitemap
                yield entry
            else:
                # For regular entries, filter for English alternates
                alternates = entry.get("alternate", [])

                if alternates:
                    for alternate in alternates:
                        if "/en/" in alternate:
                            yield {"loc": alternate}
                else:
                    yield entry

    def parse_english_page(self, response):
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

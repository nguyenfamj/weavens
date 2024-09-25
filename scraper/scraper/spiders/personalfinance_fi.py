from datetime import datetime
from scrapy import Spider
from scrapy.http import Request, Response
from scrapy.utils.sitemap import Sitemap
from ..items import ScrapeMetadata, BlogItem, OutputTakeFirstItemLoader


class PersonalFinanceFISpider(Spider):
    name = "personalfinance_fi"
    custom_settings = dict()
    sitemap_urls = ["https://www.personalfinance.fi/sitemap_index.xml"]
    total_urls_from_sitemaps = 0
    total_urls_scraped = 0

    def start_requests(self):
        for url in self.sitemap_urls:
            yield Request(url, self.parse_sitemap_index)

    def parse_sitemap_index(self, response: Response):
        sitemap = Sitemap(response.body)
        for entry in sitemap:
            url = entry["loc"]
            yield Request(url, self.parse_sitemap)

    def parse_sitemap(self, response: Response):
        sitemap = Sitemap(response.body)
        for entry in sitemap:
            url = entry["loc"]
            self.total_urls_from_sitemaps += 1
            yield Request(url, self.parse)

    def parse(self, response: Response):
        print("Extracting data from: ", response.url)

        # Check if the page is a blog post page
        # If it is a single blog post page, it must have a div with class "et_post_meta_wrapper" right after the article tag
        if not response.xpath(
            '//article[starts-with(@id, "post-")]/div[@class="et_post_meta_wrapper"]'
        ):
            return

        scrape_metadata_il = OutputTakeFirstItemLoader(
            item=ScrapeMetadata(), response=response
        )
        blog_item_il = OutputTakeFirstItemLoader(item=BlogItem(), response=response)

        # Extract scrape metadata
        scrape_metadata_il.add_value("initial_url", response.url)
        scrape_metadata_il.add_value("scraped_at", int(datetime.now().timestamp()))

        try:
            blog_item_il.add_value("site", "personalfinance.fi")
            blog_item_il.add_value("url", response.url)
            blog_item_il.add_xpath(
                "title",
                '//article[starts-with(@id, "post-")]/div[@class="et_post_meta_wrapper"]/h1[@class="entry-title"]/text()',
            )
            blog_item_il.add_xpath(
                "content_html",
                '//article[starts-with(@id, "post-")]/div[@class="entry-content"]',
            )
            # Use the processed html as the input for content_text
            blog_item_il.add_value(
                "content_text", blog_item_il.get_output_value("content_html")
            )
            # Hardcode author to "Michael Lutzeier"
            blog_item_il.add_value("author", "Michael Lutzeier")
            blog_item_il.add_value("content_type", "BLOG")
            blog_item_il.add_xpath(
                "created_at",
                '//article[starts-with(@id, "post-")]//span[@class="published"]/text()',
            )
            blog_item_il.add_xpath(
                "updated_at",
                '//article[starts-with(@id, "post-")]//span[@class="published"]/text()',
            )
            scrape_metadata_il.add_value("status", "SCRAPED")
            self.total_urls_scraped += 1
        except Exception as e:
            print("Error extracting data from: ", response.url)
            print(e)
            scrape_metadata_il.add_value("status", "ERROR")
            scrape_metadata_il.add_value("error_message", str(e))

        yield {
            **blog_item_il.load_item(),
            "scrape_metadata": dict(scrape_metadata_il.load_item()),
        }

    def closed(self, reason):
        print("Reason: ", reason)
        print("Total URLs from sitemaps: ", self.total_urls_from_sitemaps)
        print("Total URLs scraped: ", self.total_urls_scraped)

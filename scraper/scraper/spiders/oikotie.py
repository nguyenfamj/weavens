import scrapy


class OikotieSpider(scrapy.Spider):
    name = "oikotie"
    allowed_domains = ["asunnot.oikotie.fi"]
    start_urls = ["https://asunnot.oikotie.fi"]

    def parse(self, response):
        pass

# House Hunt

## Getting Started

### How to run the scraper

There are two available spiders to scrape data from the web.

| Spider names | Description                                                                           |
| ------------ | ------------------------------------------------------------------------------------- |
| oikotie_url  | To crawl the ID and URLs of properties.                                               |
| oikotie      | To crawl the detail information using the crawled URLs from the "oikotie_url" spider. |

> **Notes:**
>
> - To run the scraper, you need to run the `oikotie_url` spider first to get the URLs of the properties. Then you can run the `oikotie` spider to get the detail information, such as price, location, etc., of the properties.
> - In addition, since the spiders use the `redis` and `dynamodb` platforms, you need to run them before running the spiders.

#### Thus, run the following command in order:

1. Running the platforms needed for the scraper:

   ```bash
   # pwd
   # /path/to/house-hunt

   cd platform
   just dynamodb-up
   just redis-up
   ```

2. Running the `oikotie_url` spider:

   ```bash
   # pwd
   # /path/to/house-hunt

   cd scraper
   just crawl-url
   ```

3. Running the `oikotie` spider:

   ```bash
   # pwd
   # /path/to/house-hunt

   cd scraper
   just crawl
   ```

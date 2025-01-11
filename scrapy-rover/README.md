# Scrapy Rover

Python Scrapy project for scraping multiple websites data from the web.

## Features

- Multiple specialized spiders for different websites
- DynamoDB integration for data storage
- Redis-based URL queueing system
- S3 integration for file storage
- Playwright support for JavaScript-rendered pages
- Batch processing capabilities

## Requirements

- package-manager: [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Python 3.12
- Redis server
- AWS credentials (for production)
- DynamoDB (local or AWS)

## Installation

1. Clone the repository
2. Create a virtual environment by running `uv venv`.
3. Activate the virtual environment: `source .venv/bin/activate`.
4. Install all the dependencies by running `uv sync`.

## Available Spiders

### oikotie.fi spiders

- `oikotie_url`: To crawl the ID and URLs of properties. These ids will be saved to Redis queue for the `oikotie` spider.
- `oikotie`: To crawl the detail information using the crawled URLs from the "oikotie_url" spider.

Purpose

- Scrapes property listings from oikotie.fi and saves the data to DynamoDB.
- Collects the property details from the property listings.

### expat-finland.com spiders

- `expat_finland_url`: Collects URLs from Expat Finland website. These URLs will be scraped by `firecrawl` via `backend` endpoint and then saved to DynamoDB.

Features

- Sitemap-based crawling
- Content extraction
- Metadata parsing

### personalfinance.fi spiders

- `personalfinance_url`: Collects URLs from Personalfinance website. These URLs will be scraped by `firecrawl` via `backend` endpoint and then saved to DynamoDB.
- (Deprecated) `personalfinance`: To crawl the detail information using the crawled URLs from the "personalfinance_url" spider.This spider is deprecated and will be removed in the future, use `firecrawl` instead.

Features

- Sitemap-based crawling
- Content extraction
- Metadata parsing

### maanmittauslaitos.fi

- `maanmittauslaitos_url`: Collects URLs from Maanmittauslaitos website. These URLs will be scraped by `firecrawl` via `backend` endpoint and then saved to DynamoDB.

Features

- Sitemap-based crawling
- Content extraction
- Metadata parsing

## Configuration

### Environment Variables

```bash
AWS_REGION=eu-north-1  # Default AWS region
ENVIRONMENT=local      # local or production
REDIS_HOST=localhost   # Redis host
REDIS_PORT=6379       # Redis port
```

### DynamoDB Tables

- `Properties`: Stores property listings
- `ScrapedContent`: Stores scraped content

### Batch Processing

- `SCRAPED_CONTENT_BATCH_SIZE`: 25 (default)

## Usage

We currently promote running spiders locally, without having any instance running on cloud for MVP purpose. Please scrape the data locally and connect to DynamoDB table on cloud with proper AWS credentials.

### Local (only for development) - Run spider directly using `scrapy`

If you do not have any local DynamoDB instance, use `docker-compose up` in `platform/` to spin up a local DynamoDB instance and Redis server.

1. Make sure `dynamodb` (port 8000) and `redis` (port 6379) are running.
2. Run the spider directly using `scrapy` command.

```bash
scrapy crawl $SPIDER_NAME -a arg1=value1 -a arg2=value2
```

### Local (only for development) - Run spider via `scrapyd`

Scrapyd is a server that manages Scrapy spiders. It allows you to run spiders remotely via API interface. Read the docs [here](https://scrapyd.readthedocs.io/en/latest/overview.html).

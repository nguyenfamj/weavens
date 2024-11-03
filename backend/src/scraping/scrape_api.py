import os

from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))


def firecrawl_scrape(
    url: str,
    exclude_tags: list[str] = ["input", "script"],
    include_tags: list[str] = [],
):
    params = {
        "formats": ["markdown", "links", "html"],
        "excludeTags": exclude_tags,
    }

    if include_tags:
        params["includeTags"] = include_tags

    return app.scrape_url(
        url=url,
        params=params,
    )

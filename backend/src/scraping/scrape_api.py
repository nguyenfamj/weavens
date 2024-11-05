import os

from firecrawl import FirecrawlApp


def get_firecrawl_app():
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("No API key provided")
    return FirecrawlApp(api_key=api_key)


def firecrawl_scrape(
    url: str,
    exclude_tags: list[str] = ["input", "script"],
    include_tags: list[str] = [],
):
    app = get_firecrawl_app()
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

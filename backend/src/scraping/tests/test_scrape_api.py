import pytest
from unittest.mock import patch

from src.scraping.scrape_api import firecrawl_scrape, get_firecrawl_app


@pytest.fixture
def mock_deps_scrape_api():
    with patch("src.scraping.scrape_api.FirecrawlApp") as mock_firecrawl_app, patch(
        "src.scraping.scrape_api.settings"
    ) as mock_settings:
        yield {
            "mock_firecrawl_app": mock_firecrawl_app,
            "mock_settings": mock_settings,
        }


@pytest.mark.unit
class TestScrapeApi:
    def test_get_firecrawl_app_should_return_firecrawl_app(self, mock_deps_scrape_api):
        firecrawl_app = get_firecrawl_app()
        mock_deps_scrape_api["mock_settings"].FIRECRAWL_API_KEY = "test-api-key"
        assert firecrawl_app is not None

    def test_get_firecrawl_app_should_raise_error_when_no_api_key(
        self, mock_deps_scrape_api
    ):
        mock_deps_scrape_api["mock_settings"].FIRECRAWL_API_KEY = None
        with pytest.raises(ValueError):
            get_firecrawl_app()

    def test_firecrawl_scrape_should_return_markdown_html_and_metadata(
        self, mock_deps_scrape_api
    ):
        firecrawl_app = mock_deps_scrape_api["mock_firecrawl_app"].return_value
        firecrawl_app.scrape_url.return_value = {
            "markdown": "test markdown",
            "html": "test html",
            "metadata": {},
        }

        result = firecrawl_scrape(url="https://test.com")
        assert result == {
            "markdown": "test markdown",
            "html": "test html",
            "metadata": {},
        }
        firecrawl_app.scrape_url.assert_called_once_with(
            url="https://test.com",
            params={
                "formats": ["markdown", "links", "html"],
                "excludeTags": ["input", "script"],
            },
        )

    def test_firecrawl_scrape_should_add_include_tags_when_provided(
        self, mock_deps_scrape_api
    ):
        firecrawl_app = mock_deps_scrape_api["mock_firecrawl_app"].return_value

        firecrawl_scrape(url="https://test.com", include_tags=["test-tag"])
        firecrawl_app.scrape_url.assert_called_once_with(
            url="https://test.com",
            params={
                "formats": ["markdown", "links", "html"],
                "excludeTags": ["input", "script"],
                "includeTags": ["test-tag"],
            },
        )

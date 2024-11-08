import pytest
from unittest.mock import patch
from src.scraping.background import scrape_urls_task

from src.scraping.schemas import (
    ScrapedContentStatus,
    ScrapeJobStatus,
    UpdateScrapedContentFromJobParams,
)


@pytest.fixture
def mock_deps_scrape_urls_task():
    with patch(
        "src.scraping.background.firecrawl_scrape"
    ) as mock_firecrawl_scrape, patch(
        "src.scraping.background.update_scraped_content_status_from_job"
    ) as mock_update_scraped_content_status_from_job, patch(
        "src.scraping.background.update_scraped_content_from_job"
    ) as mock_update_scraped_content_from_job, patch(
        "src.scraping.background.update_scrape_job_status"
    ) as mock_update_scrape_job_status, patch(
        "src.scraping.background.EmbeddingService"
    ) as mock_embedding_service:
        yield {
            "mock_firecrawl_scrape": mock_firecrawl_scrape,
            "mock_update_scraped_content_status_from_job": mock_update_scraped_content_status_from_job,
            "mock_update_scraped_content_from_job": mock_update_scraped_content_from_job,
            "mock_update_scrape_job_status": mock_update_scrape_job_status,
            "mock_embedding_service": mock_embedding_service,
        }


@pytest.mark.unit
class TestScrapeUrlTask:
    def test_scrape_single_url(self, mock_deps_scrape_urls_task):
        mock_deps_scrape_urls_task["mock_firecrawl_scrape"].return_value = {
            "markdown": "test markdown",
            "html": "test html",
            "metadata": {},
        }
        scrape_urls_task(urls=["https://test.com"], job_id="Test123")
        mock_deps_scrape_urls_task[
            "mock_update_scraped_content_from_job"
        ].assert_called_once_with(
            UpdateScrapedContentFromJobParams(
                url="https://test.com",
                content_md5="test markdown",
                content_html="test html",
                status=ScrapedContentStatus.SCRAPED,
                last_scrape_job_id="Test123",
                metadata={},
            )
        )

        mock_deps_scrape_urls_task[
            "mock_update_scrape_job_status"
        ].assert_called_once_with(
            job_id="Test123",
            status=ScrapeJobStatus.COMPLETED,
            total_urls=1,
            completed_urls=1,
        )

    def test_failed_scrape_single_url(self, mock_deps_scrape_urls_task):
        mock_deps_scrape_urls_task["mock_firecrawl_scrape"].side_effect = Exception(
            "Test error"
        )
        scrape_urls_task(urls=["https://test.com"], job_id="Test123")

        mock_deps_scrape_urls_task[
            "mock_update_scraped_content_status_from_job"
        ].assert_called_once_with(
            "https://test.com", "Test123", ScrapedContentStatus.FAILED
        )

    def test_partially_completed_job(self, mock_deps_scrape_urls_task):
        mock_deps_scrape_urls_task["mock_firecrawl_scrape"].side_effect = [
            {"markdown": "test_md", "html": "test_html", "metadata": {}},
            Exception("Scrape failed"),
        ]
        scrape_urls_task(
            urls=["https://test.com", "https://test2.com"], job_id="Test123"
        )

        mock_deps_scrape_urls_task[
            "mock_update_scrape_job_status"
        ].assert_called_once_with(
            job_id="Test123",
            status=ScrapeJobStatus.PARTIALLY_COMPLETED,
            total_urls=2,
            completed_urls=1,
        )

    def test_mark_job_as_failed_when_cannot_update_status(
        self, mock_deps_scrape_urls_task
    ):
        mock_deps_scrape_urls_task["mock_firecrawl_scrape"].return_value = {
            "markdown": "test markdown",
            "html": "test html",
            "metadata": {},
        }
        mock_deps_scrape_urls_task[
            "mock_update_scraped_content_from_job"
        ].side_effect = Exception("Test error")
        scrape_urls_task(urls=["https://test.com"], job_id="Test123")

        mock_deps_scrape_urls_task[
            "mock_update_scrape_job_status"
        ].assert_called_once_with(
            job_id="Test123",
            status=ScrapeJobStatus.FAILED,
            total_urls=1,
            completed_urls=0,
        )

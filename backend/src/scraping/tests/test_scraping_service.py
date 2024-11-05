import pytest
from unittest.mock import patch, ANY
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

from src.scraping.service import (
    create_scrape_job_by_type,
    get_in_progress_jobs_by_type,
    update_scrape_job_status,
    get_all_web_document_urls_without_content,
    update_scraped_content_status_from_job,
    update_scraped_content_from_job,
)
from src.scraping.schemas import (
    ScrapedContentStatus,
    ScrapeJobStatus,
    UpdateScrapedContentFromJobParams,
    DocumentType,
)


@pytest.fixture
def mock_deps_scraping_service():
    with patch("src.scraping.service.uuid4") as mock_uuid4, patch(
        "src.scraping.service.scrape_jobs_table"
    ) as mock_scrape_jobs_table, patch(
        "src.scraping.service.scraped_content_table"
    ) as mock_scraped_content_table, patch(
        "src.scraping.service.logger"
    ) as mock_logger:
        yield {
            "mock_uuid4": mock_uuid4,
            "mock_scrape_jobs_table": mock_scrape_jobs_table,
            "mock_scraped_content_table": mock_scraped_content_table,
            "mock_logger": mock_logger,
        }


@pytest.mark.unit
class TestScrapingService:
    def test_create_scrape_job_by_type_should_return_job_with_id(
        self, mock_deps_scraping_service
    ):
        mock_deps_scraping_service["mock_uuid4"].return_value = "test-id"
        scrape_job = create_scrape_job_by_type(DocumentType.WEB_DOCUMENT)

        mock_deps_scraping_service[
            "mock_scrape_jobs_table"
        ].put_item.assert_called_once_with(
            Item={
                "id": "test-id",
                "type": DocumentType.WEB_DOCUMENT,
                "status": ScrapeJobStatus.IN_PROGRESS,
                "initiated_at": ANY,
                "created_at": ANY,
                "completed_at": None,
                "total_urls": None,
                "completed_urls": None,
            }
        )
        assert scrape_job.id == "test-id"

    def test_create_scrape_job_by_type_should_raise_error_when_cannot_create_job(
        self, mock_deps_scraping_service
    ):
        mock_deps_scraping_service[
            "mock_scrape_jobs_table"
        ].put_item.side_effect = ClientError(
            operation_name="put_item",
            error_response={
                "Error": {"Code": "TestErrorCode", "Message": "Test message"}
            },
        )
        with pytest.raises(ClientError):
            create_scrape_job_by_type(DocumentType.WEB_DOCUMENT)
        mock_deps_scraping_service["mock_logger"].error.assert_called_once()

    def test_get_in_progress_jobs_by_type_should_return_jobs_from_database(
        self, mock_deps_scraping_service
    ):
        mock_deps_scraping_service["mock_scrape_jobs_table"].query.return_value = {
            "Items": [
                {
                    "id": "test-id",
                    "type": DocumentType.WEB_DOCUMENT,
                    "status": ScrapeJobStatus.IN_PROGRESS,
                }
            ]
        }
        jobs = get_in_progress_jobs_by_type(DocumentType.WEB_DOCUMENT)
        mock_deps_scraping_service[
            "mock_scrape_jobs_table"
        ].query.assert_called_once_with(
            IndexName="TypeByStatusGSI",
            KeyConditionExpression=Key("type").eq(DocumentType.WEB_DOCUMENT)
            & Key("status").eq(ScrapeJobStatus.IN_PROGRESS),
        )
        assert jobs == [
            {
                "id": "test-id",
                "type": DocumentType.WEB_DOCUMENT,
                "status": ScrapeJobStatus.IN_PROGRESS,
            }
        ]

    def test_get_in_progress_jobs_by_type_should_raise_error_when_cannot_get_jobs(
        self, mock_deps_scraping_service
    ):
        mock_deps_scraping_service[
            "mock_scrape_jobs_table"
        ].query.side_effect = ClientError(
            operation_name="query",
            error_response={
                "Error": {"Code": "TestErrorCode", "Message": "Test message"}
            },
        )
        with pytest.raises(ClientError):
            get_in_progress_jobs_by_type(DocumentType.WEB_DOCUMENT)
        mock_deps_scraping_service["mock_logger"].error.assert_called_once()

    def test_update_scrape_job_status_should_update_job_status_in_database(
        self, mock_deps_scraping_service
    ):
        update_scrape_job_status(
            job_id="test-id",
            status=ScrapeJobStatus.COMPLETED,
            total_urls=1,
            completed_urls=1,
        )
        mock_deps_scraping_service[
            "mock_scrape_jobs_table"
        ].update_item.assert_called_once()

    def test_update_scrape_job_status_should_raise_error_when_cannot_update_job(
        self, mock_deps_scraping_service
    ):
        mock_deps_scraping_service[
            "mock_scrape_jobs_table"
        ].update_item.side_effect = ClientError(
            operation_name="update_item",
            error_response={
                "Error": {"Code": "TestErrorCode", "Message": "Test message"}
            },
        )
        with pytest.raises(ClientError):
            update_scrape_job_status(
                job_id="test-id",
                status=ScrapeJobStatus.COMPLETED,
                total_urls=1,
                completed_urls=1,
            )
        mock_deps_scraping_service["mock_logger"].error.assert_called_once()

    def test_get_all_web_document_urls_without_content_should_return_urls_from_database(
        self, mock_deps_scraping_service
    ):
        mock_deps_scraping_service["mock_scraped_content_table"].query.side_effect = [
            {
                "Items": [
                    {"url": "https://test1.com"},
                    {"url": "https://test2.com"},
                ]
            },
            {
                "Items": [
                    {"url": "https://test3.com"},
                ]
            },
        ]

        urls = get_all_web_document_urls_without_content()

        assert urls == ["https://test1.com", "https://test2.com", "https://test3.com"]
        assert (
            mock_deps_scraping_service["mock_scraped_content_table"].query.call_count
            == 2
        )

    def test_get_all_web_document_urls_without_content_should_raise_error_when_cannot_query_database(
        self, mock_deps_scraping_service
    ):
        mock_deps_scraping_service[
            "mock_scraped_content_table"
        ].query.side_effect = ClientError(
            operation_name="query",
            error_response={
                "Error": {"Code": "TestErrorCode", "Message": "Test message"}
            },
        )
        with pytest.raises(ClientError):
            get_all_web_document_urls_without_content()
        mock_deps_scraping_service["mock_logger"].error.assert_called_once()

    def test_update_scraped_content_status_from_job_should_update_status_in_database(
        self, mock_deps_scraping_service
    ):
        update_scraped_content_status_from_job(
            url="https://test.com",
            job_id="test-id",
            status=ScrapedContentStatus.SCRAPED,
        )
        mock_deps_scraping_service[
            "mock_scraped_content_table"
        ].update_item.assert_called_once()

    def test_update_scraped_content_status_from_job_should_raise_error_when_cannot_update_status(
        self, mock_deps_scraping_service
    ):
        mock_deps_scraping_service[
            "mock_scraped_content_table"
        ].update_item.side_effect = ClientError(
            operation_name="update_item",
            error_response={
                "Error": {"Code": "TestErrorCode", "Message": "Test message"}
            },
        )
        with pytest.raises(ClientError):
            update_scraped_content_status_from_job(
                url="https://test.com",
                job_id="test-id",
                status=ScrapedContentStatus.SCRAPED,
            )
        mock_deps_scraping_service["mock_logger"].error.assert_called_once()

    def test_update_scraped_content_from_job_should_update_content_in_database(
        self, mock_deps_scraping_service
    ):
        params = UpdateScrapedContentFromJobParams(
            url="https://test.com",
            content_md5="test-md5",
            content_html="test-html",
            status=ScrapedContentStatus.SCRAPED,
            last_scrape_job_id="test-job-id",
            metadata={},
        )
        update_scraped_content_from_job(params)
        mock_deps_scraping_service[
            "mock_scraped_content_table"
        ].update_item.assert_called_once_with(
            Key={"url": params.url},
            UpdateExpression="set content_md5 = :content_md5, content_html = :content_html, #status = :status, last_scrape_job_id = :last_scrape_job_id, metadata = :metadata, last_scraped_at = :last_scraped_at",
            ExpressionAttributeValues={
                ":content_md5": params.content_md5,
                ":content_html": params.content_html,
                ":status": params.status,
                ":last_scrape_job_id": params.last_scrape_job_id,
                ":metadata": params.metadata,
                ":last_scraped_at": ANY,
            },
            ExpressionAttributeNames={"#status": "status"},
        )

    def test_update_scraped_content_from_job_should_raise_error_when_cannot_update_content(
        self, mock_deps_scraping_service
    ):
        params = UpdateScrapedContentFromJobParams(
            url="https://test.com",
            content_md5="test-md5",
            content_html="test-html",
            status=ScrapedContentStatus.SCRAPED,
            last_scrape_job_id="test-job-id",
            metadata={},
        )
        mock_deps_scraping_service[
            "mock_scraped_content_table"
        ].update_item.side_effect = ClientError(
            operation_name="update_item",
            error_response={
                "Error": {"Code": "TestErrorCode", "Message": "Test message"}
            },
        )
        with pytest.raises(ClientError):
            update_scraped_content_from_job(params)
        mock_deps_scraping_service["mock_logger"].error.assert_called_once()

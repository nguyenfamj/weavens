from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from uuid import uuid4
from datetime import datetime

from ..db import dynamodb
from ..logging import Logger
from .schemas import (
    DocumentType,
    ScrapeJob,
    ScrapeJobStatus,
    ScrapedContentStatus,
    UpdateScrapedContentFromJobParams,
)

logger = Logger(__name__).logger

scrape_jobs_table = dynamodb.Table("ScrapeJobs")
scraped_content_table = dynamodb.Table("ScrapedContent")


async def create_scrape_job_by_type(type: DocumentType) -> ScrapeJob:
    """
    Create a new scrape job
    New jobs are created in default status of "IN_PROGRESS"
    """
    current_time = datetime.now().isoformat()
    item = ScrapeJob(
        id=str(uuid4()),
        type=type,
        status=ScrapeJobStatus.IN_PROGRESS,
        initiated_at=current_time,
        created_at=current_time,
    )
    logger.info("Creating scrape job with type %s: %s", type, item.model_dump())
    try:
        scrape_jobs_table.put_item(Item=item.model_dump())
    except ClientError as err:
        logger.error(
            "Error creating scrape job with type %s: %s: %s",
            type,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise
    else:
        return item


async def get_in_progress_jobs_by_type(type: DocumentType) -> list[str]:
    """
    Get all the in progress scraping jobs by job type
    In progress jobs are those that has a status of "IN_PROGRESS"
    """
    try:
        response = scrape_jobs_table.query(
            IndexName="TypeByStatusGSI",
            KeyConditionExpression=Key("type").eq(type)
            & Key("status").eq(ScrapeJobStatus.IN_PROGRESS),
        )
    except ClientError as err:
        logger.error(
            "Error getting in-progress jobs with type %s: %s: %s",
            type,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise
    else:
        return response["Items"]


async def update_scrape_job_status(
    job_id: str,
    status: ScrapeJobStatus,
    total_urls: int | None = None,
    completed_urls: int | None = None,
):
    try:
        scrape_jobs_table.update_item(
            Key={"id": job_id},
            UpdateExpression="set #status = :status, completed_at = :completed_at, total_urls = :total_urls, completed_urls = :completed_urls",
            ExpressionAttributeValues={
                ":status": status,
                ":completed_at": datetime.now().isoformat(),
                ":total_urls": total_urls,
                ":completed_urls": completed_urls,
            },
            ExpressionAttributeNames={"#status": "status"},
        )
    except ClientError as err:
        logger.error(
            "Error updating scrape job status %s: %s: %s",
            job_id,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )


async def get_all_web_document_urls_without_content() -> list[str]:
    """
    Get all the urls that do not have content_html or content_md5
    """
    try:
        not_scraped_response = scraped_content_table.query(
            IndexName="StatusByTypeGSI",
            KeyConditionExpression=Key("status").eq(ScrapedContentStatus.NOT_SCRAPED)
            & Key("type").eq(DocumentType.WEB_DOCUMENT),
        )

        failed_response = scraped_content_table.query(
            IndexName="StatusByTypeGSI",
            KeyConditionExpression=Key("status").eq(ScrapedContentStatus.FAILED)
            & Key("type").eq(DocumentType.WEB_DOCUMENT),
        )
    except ClientError as err:
        logger.error(
            "Error getting all urls without content: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise
    else:
        urls = []
        urls.extend([item["url"] for item in not_scraped_response["Items"]])
        urls.extend([item["url"] for item in failed_response["Items"]])
        return urls


async def update_scraped_content_status_from_job(
    url: str, job_id: str, status: ScrapedContentStatus
):
    try:
        scraped_content_table.update_item(
            Key={"url": url},
            UpdateExpression="set #status = :status, last_scrape_job_id = :job_id, last_scraped_at = :last_scraped_at",
            ExpressionAttributeValues={
                ":status": status,
                ":job_id": job_id,
                ":last_scraped_at": datetime.now().isoformat(),
            },
            ExpressionAttributeNames={"#status": "status"},
        )
    except ClientError as err:
        logger.error(
            "Error updating scraped content status from job %s: %s: %s",
            job_id,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise


async def update_scraped_content_from_job(params: UpdateScrapedContentFromJobParams):
    try:
        scraped_content_table.update_item(
            Key={"url": params.url},
            UpdateExpression="set content_md5 = :content_md5, content_html = :content_html, #status = :status, last_scrape_job_id = :last_scrape_job_id, metadata = :metadata, last_scraped_at = :last_scraped_at",
            ExpressionAttributeValues={
                ":content_md5": params.content_md5,
                ":content_html": params.content_html,
                ":status": params.status,
                ":metadata": params.metadata,
                ":last_scrape_job_id": params.last_scrape_job_id,
                ":last_scraped_at": datetime.now().isoformat(),
            },
            ExpressionAttributeNames={"#status": "status"},
        )
    except ClientError as err:
        logger.error(
            "Error updating scraped content from job %s: %s: %s",
            params.last_scrape_job_id,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise

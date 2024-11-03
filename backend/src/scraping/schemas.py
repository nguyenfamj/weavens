from pydantic import BaseModel, Field
from enum import Enum

from ..schemas import BaseResponse


class DocumentType(str, Enum):
    WEB_DOCUMENT = "web_document"
    MEDIA = "media"


class ScrapeJobStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ScrapedContentStatus(str, Enum):
    SCRAPED = "SCRAPED"
    NOT_SCRAPED = "NOT_SCRAPED"
    FAILED = "FAILED"


class ScrapedContentMimeType(str, Enum):
    PDF = "application/pdf"


class CreateScrapeJobRequest(BaseModel):
    type: DocumentType


class ScrapeJob(BaseModel):
    id: str
    type: DocumentType
    status: ScrapeJobStatus
    initiated_at: str
    created_at: str
    completed_at: str | None = None
    total_urls: int | None = None
    completed_urls: int | None = None


class ScrapedContent(BaseModel):
    url: str
    type: DocumentType
    content_md5: str | None = None
    content_html: str | None = None
    mime_type: ScrapedContentMimeType | None = None
    status: ScrapedContentStatus
    last_scrape_job_id: str | None = None
    last_scraped_at: str | None = None
    metadata: dict | None = None


class TriggerScrapeJobResponse(BaseResponse):
    job_id: str | None = Field(
        description="The id of the scrape job created after triggering"
    )
    status: ScrapeJobStatus | None = Field(description="The status of the scrape job")


class UpdateScrapedContentFromJobParams(BaseModel):
    url: str
    content_md5: str | None = None
    content_html: str | None = None
    status: ScrapedContentStatus
    last_scrape_job_id: str
    metadata: dict | None = None

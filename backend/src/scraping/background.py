from langchain.text_splitter import RecursiveCharacterTextSplitter

from .scrape_api import firecrawl_scrape
from .service import (
    update_scraped_content_status_from_job,
    update_scraped_content_from_job,
    update_scrape_job_status,
)
from src.embedding.service import EmbeddingService
from src.core.logging import Logger

from .schemas import (
    ScrapedContentStatus,
    ScrapeJobStatus,
    UpdateScrapedContentFromJobParams,
)

logger = Logger(__name__).logger


def scrape_urls_task(urls: list[str], job_id: str):
    embedding_service = EmbeddingService()
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        keep_separator=True,
    )

    job_status = ScrapeJobStatus.IN_PROGRESS
    completed_urls = 0
    try:
        for i, url in enumerate(urls):
            logger.info(
                "(ScrapedJobs#%s)[%s/%s] Scraping url %s ",
                job_id,
                i + 1,
                len(urls),
                url,
            )

            try:
                scraped_content = firecrawl_scrape(url)
            except Exception as e:
                logger.error("Error scraping url %s: %s", url, e)
                update_scraped_content_status_from_job(
                    url, job_id, ScrapedContentStatus.FAILED
                )
                continue

            # Save the scraped content to the database
            update_scraped_content_from_job(
                UpdateScrapedContentFromJobParams(
                    url=url,
                    status=ScrapedContentStatus.SCRAPED,
                    content_md5=scraped_content["markdown"],
                    content_html=scraped_content["html"],
                    last_scrape_job_id=job_id,
                    metadata=scraped_content["metadata"],
                )
            )

            scraped_content_metadata = scraped_content["metadata"]

            # Save embedded contents
            # TODO: This should be a temporary solution until we can handle this with DynamoDB stream
            text_chunks = text_splitter.split_text(scraped_content["markdown"])

            logger.info("Adding %s chunks to vector collection", len(text_chunks))
            embedding_service.add_text_chunks_to_collection(
                text_chunks=text_chunks,
                file_name=url,
                shared_metadata={
                    "title": scraped_content_metadata.get("title"),
                    "language": scraped_content_metadata.get("language"),
                    "sourceURL": scraped_content_metadata.get("sourceURL"),
                    "author": scraped_content_metadata.get("author"),
                },
            )

            # Increment the completed urls counter
            completed_urls += 1

            # Update the job status to partially completed if not all urls are completed
            job_status = (
                ScrapeJobStatus.PARTIALLY_COMPLETED
                if completed_urls < len(urls)
                else ScrapeJobStatus.COMPLETED
            )

        # Update the job status to completed
        update_scrape_job_status(
            job_id=job_id,
            status=job_status,
            total_urls=len(urls),
            completed_urls=completed_urls,
        )
    except Exception as e:
        logger.error("Error while executing scrape job %s: %s", job_id, e)
        update_scrape_job_status(
            job_id=job_id,
            status=ScrapeJobStatus.FAILED,
            total_urls=len(urls),
            completed_urls=completed_urls,
        )

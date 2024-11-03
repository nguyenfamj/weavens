from .scrape_api import firecrawl_scrape
from .service import (
    update_scraped_content_status_from_job,
    update_scraped_content_from_job,
    update_scrape_job_status,
)
from ..logging import Logger
from .schemas import (
    ScrapedContentStatus,
    ScrapeJobStatus,
    UpdateScrapedContentFromJobParams,
)

logger = Logger(__name__).logger


async def scrape_urls_task(urls: list[str], job_id: str):
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
                await update_scraped_content_status_from_job(
                    url, job_id, ScrapedContentStatus.FAILED
                )
                continue

            # Save the scraped content to the database
            await update_scraped_content_from_job(
                UpdateScrapedContentFromJobParams(
                    url=url,
                    status=ScrapedContentStatus.SCRAPED,
                    content_md5=scraped_content["markdown"],
                    content_html=scraped_content["html"],
                    last_scrape_job_id=job_id,
                    metadata=scraped_content["metadata"],
                )
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
        await update_scrape_job_status(
            job_id=job_id,
            status=job_status,
            total_urls=len(urls),
            completed_urls=completed_urls,
        )
    except Exception as e:
        logger.error("Error while executing scrape job %s: %s", job_id, e)
        await update_scrape_job_status(
            job_id=job_id,
            status=ScrapeJobStatus.FAILED,
            total_urls=len(urls),
            completed_urls=completed_urls,
        )

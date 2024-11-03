from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from .schemas import DocumentType, ScrapeJobStatus, TriggerScrapeJobResponse
from .background import scrape_urls_task
from .service import (
    get_in_progress_jobs_by_type,
    get_all_web_document_urls_without_content,
    create_scrape_job_by_type,
    update_scrape_job_status,
)

router = APIRouter(tags=["scraping"])


@router.post("/trigger/webdocs", status_code=status.HTTP_202_ACCEPTED)
async def scrape_web_documents(background_tasks: BackgroundTasks):
    active_jobs = get_in_progress_jobs_by_type(DocumentType.WEB_DOCUMENT)

    if len(active_jobs) > 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="There are active scraping tasks. Please try again later.",
        )

    scrape_job = create_scrape_job_by_type(DocumentType.WEB_DOCUMENT)

    try:
        urls = get_all_web_document_urls_without_content()
    except Exception as e:
        update_scrape_job_status(
            job_id=scrape_job.id,
            status=ScrapeJobStatus.FAILED,
        )
        raise HTTPException(status_code=500, detail=str(e))

    background_tasks.add_task(scrape_urls_task, urls[:5], scrape_job.id)

    return TriggerScrapeJobResponse(
        status_code=status.HTTP_202_ACCEPTED,
        job_id=scrape_job.id,
        status=scrape_job.status,
    )

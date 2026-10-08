import os
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from .models import CertificateJob, RecipientRecord
from .schemas import BulkJobCreateRequest, JobStatusResponse
from .services import process_bulk_certificates

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bulk Certificate Generator API",
    version="1.0.0",
    description="Asynchronous bulk certificate generator with progress tracking."
)

os.makedirs("static/certificates", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/api/v1/certificates/bulk", status_code=status.HTTP_202_ACCEPTED)
def submit_bulk_job(
    payload: BulkJobCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submits a list of recipients for bulk certificate generation."""
    new_job = CertificateJob(total_count=len(payload.recipients))
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    for item in payload.recipients:
        rec = RecipientRecord(job_id=new_job.id, name=item.name, course_name=item.course_name)
        db.add(rec)
    db.commit()

    background_tasks.add_task(process_bulk_certificates, new_job.id)

    return {
        "job_id": new_job.id,
        "status": new_job.status,
        "message": f"Job accepted with {len(payload.recipients)} recipients.",
        "status_url": f"/api/v1/certificates/jobs/{new_job.id}"
    }

@app.get("/api/v1/certificates/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """Check the status and recipient-level results of a generation job."""
    job = db.query(CertificateJob).filter(CertificateJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job.id,
        "status": job.status,
        "total_count": job.total_count,
        "success_count": job.success_count,
        "failed_count": job.failed_count,
        "created_at": job.created_at,
        "recipients": job.recipients
    }

@app.get("/api/v1/certificates/{recipient_id}/download")
def download_certificate(recipient_id: str, db: Session = Depends(get_db)):
    """Directly download a generated certificate."""
    rec = db.query(RecipientRecord).filter(RecipientRecord.id == recipient_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recipient record not found")
    if rec.status != "SUCCESS" or not rec.file_path:
        raise HTTPException(status_code=400, detail="Certificate is not available or generation failed")

    local_path = rec.file_path.lstrip("/")
    if not os.path.exists(local_path):
        raise HTTPException(status_code=404, detail="File missing on server")

    return FileResponse(local_path, media_type="image/png", filename=f"certificate_{rec.name}.png")
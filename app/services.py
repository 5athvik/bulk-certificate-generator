import os
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import CertificateJob, RecipientRecord
from .template_generator import generate_certificate_image, OUTPUT_DIR

def process_bulk_certificates(job_id: str):
    db: Session = SessionLocal()
    try:
        job = db.query(CertificateJob).filter(CertificateJob.id == job_id).first()
        if not job:
            return

        job.status = "PROCESSING"
        db.commit()

        successes = 0
        failures = 0
        recipients = db.query(RecipientRecord).filter(RecipientRecord.job_id == job_id).all()

        for rec in recipients:
            try:
                # Simulates individual failure condition for testing edge cases
                if "error_test" in rec.name.lower():
                    raise ValueError("Simulated unexpected generation failure.")

                filename = f"{rec.id}.png"
                out_path = os.path.join(OUTPUT_DIR, filename)

                generate_certificate_image(rec.name, rec.course_name, out_path)

                rec.status = "SUCCESS"
                rec.file_path = f"/static/certificates/{filename}"
                successes += 1
            except Exception as exc:
                rec.status = "FAILED"
                rec.error_message = str(exc)
                failures += 1

            db.commit()

        job.success_count = successes
        job.failed_count = failures
        job.status = "COMPLETED"
        db.commit()
    finally:
        db.close()
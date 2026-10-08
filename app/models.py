import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

def utc_now():
    return datetime.now(timezone.utc)

class CertificateJob(Base):
    __tablename__ = "certificate_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String, default="PENDING")  # PENDING, PROCESSING, COMPLETED
    total_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    recipients = relationship("RecipientRecord", back_populates="job", cascade="all, delete-orphan")


class RecipientRecord(Base):
    __tablename__ = "recipient_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("certificate_jobs.id"), nullable=False)
    name = Column(String, nullable=False)
    course_name = Column(String, nullable=False)
    status = Column(String, default="PENDING")  # PENDING, SUCCESS, FAILED
    file_path = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)

    job = relationship("CertificateJob", back_populates="recipients")
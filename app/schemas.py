from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class RecipientInput(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Recipient full name")
    course_name: str = Field(..., min_length=2, max_length=150, description="Course or event title")

class BulkJobCreateRequest(BaseModel):
    recipients: List[RecipientInput] = Field(..., min_length=1, description="List of recipients")

class RecipientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    course_name: str
    status: str
    file_path: Optional[str] = None
    error_message: Optional[str] = None

class JobStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    status: str
    total_count: int
    success_count: int
    failed_count: int
    created_at: datetime
    recipients: List[RecipientResponse]
# Bulk Certificate Generator API

An asynchronous backend REST API built with FastAPI, SQLite, and Pillow to generate, track, and retrieve event certificates in bulk.

## Features
- **Bulk Processing:** Accepts large batches of recipient records and processes them via non-blocking background workers.
- **Fault-Tolerant & Isolated Failures:** A failure generating any individual certificate does not abort the rest of the job.
- **Status & Progress Tracking:** Immediately returns `202 Accepted` with a job ID and tracking endpoint.
- **Direct Retrieval:** Exposes endpoints to inspect job progress and download individual generated certificate images.
- **Input Validation:** Enforces strict payload validation with clear Pydantic schemas.

---

## Tech Stack
- **Language:** Python 3.12+ / 3.14
- **Framework:** FastAPI
- **Database / ORM:** SQLite + SQLAlchemy
- **Image Generation:** Pillow (PIL)
- **Testing:** pytest + httpx (FastAPI TestClient)

---

## Setup & Running the Application

### 1. Clone the repository
```bash
git clone <your-github-repo-url>
cd bulk-certificate-generator
```

### 2. Set up virtual environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the server
```bash
uvicorn app.main:app --reload
```
Interactive Swagger documentation will be live at: `http://127.0.0.1:8000/docs`.

---

## API Usage Examples

### 1. Submit Bulk Certificate Job
- **POST** `/api/v1/certificates/bulk`
- **Request Body:**
```json
{
  "recipients": [
    { "name": "John Doe", "course_name": "Full Stack Cloud Architecture" },
    { "name": "Jane Smith", "course_name": "Full Stack Cloud Architecture" }
  ]
}
```
- **Response (`202 Accepted`):**
```json
{
  "job_id": "97e6bece-2a1d-44aa-9cbf-9a084c7f12e8",
  "status": "PENDING",
  "message": "Job accepted with 2 recipients.",
  "status_url": "/api/v1/certificates/jobs/97e6bece-2a1d-44aa-9cbf-9a084c7f12e8"
}
```

### 2. Check Job Status
- **GET** `/api/v1/certificates/jobs/{job_id}`
- **Response (`200 OK`):**
```json
{
  "job_id": "97e6bece-2a1d-44aa-9cbf-9a084c7f12e8",
  "status": "COMPLETED",
  "total_count": 2,
  "success_count": 2,
  "failed_count": 0,
  "created_at": "2026-10-08T10:30:00Z",
  "recipients": [
    {
      "id": "c1f7be0b-b15c-4fbf-9d21-4d3ca9d54e4c",
      "name": "John Doe",
      "course_name": "Full Stack Cloud Architecture",
      "status": "SUCCESS",
      "file_path": "/static/certificates/c1f7be0b-b15c-4fbf-9d21-4d3ca9d54e4c.png",
      "error_message": null
    }
  ]
}
```

### 3. Download Certificate
- **GET** `/api/v1/certificates/{recipient_id}/download`
- Returns the rendered high-resolution PNG certificate directly as an attachment.

---

## Running Automated Tests
```bash
pytest tests/test_api.py -v
```

---

## Architectural & Design Decisions
1. **Asynchronous Background Processing:** Heavy canvas rendering in bulk would cause HTTP timeouts if executed synchronously. FastAPI's `BackgroundTasks` processes jobs out-of-band without introducing heavy third-party broker dependencies (such as Redis/Celery) for the evaluator.
2. **Failure Isolation:** Each recipient in the worker loop is wrapped in isolated exception boundaries. If one record produces an error, it is recorded with an error message and the loop continues processing subsequent recipients.
3. **Pillow Canvas Rendering:** Used pure Pillow drawing primitives over headless browser HTML-to-PDF converters (e.g., WeasyPrint, Puppeteer) to minimize system dependencies, binary overhead, and memory consumption.
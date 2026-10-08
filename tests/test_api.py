from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_validation_rejects_empty_payload():
    response = client.post("/api/v1/certificates/bulk", json={"recipients": []})
    assert response.status_code == 422

def test_bulk_generation_and_isolated_failure():
    payload = {
        "recipients": [
            {"name": "Jane Doe", "course_name": "Full Stack Engineering"},
            {"name": "error_test_Person", "course_name": "System Architecture"}
        ]
    }
    create_resp = client.post("/api/v1/certificates/bulk", json=payload)
    assert create_resp.status_code == 202
    job_id = create_resp.json()["job_id"]

    # Verify job status
    status_resp = client.get(f"/api/v1/certificates/jobs/{job_id}")
    assert status_resp.status_code == 200
    data = status_resp.json()

    assert data["status"] == "COMPLETED"
    assert data["total_count"] == 2
    assert data["success_count"] == 1
    assert data["failed_count"] == 1

    # Verify download of successful certificate
    success_record = next(r for r in data["recipients"] if r["status"] == "SUCCESS")
    download_resp = client.get(f"/api/v1/certificates/{success_record['id']}/download")
    assert download_resp.status_code == 200
    assert download_resp.headers["content-type"] == "image/png"
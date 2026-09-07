from tests.conftest import login_as

ROW = {
    "attendance_date": "2026-09-01",
    "worker_name": "Amit Shah",
    "input_parts": 450,
    "total_working_hours": 8,
    "machine_stopped_time": 1,
    "attendance_status": "PRESENT",
    "remarks": "",
}


def test_supervisor_cannot_access_reports(client, supervisor_user):
    login_as(client, supervisor_user)
    resp = client.get("/api/reports/daily?date=2026-09-01")
    assert resp.status_code == 403


def test_daily_report_returns_matching_records(client, supervisor_user, admin_user):
    login_as(client, supervisor_user)
    client.post("/api/attendance", json=ROW)
    client.post("/api/attendance", json={**ROW, "attendance_date": "2026-09-02", "worker_name": "Raj Patel"})

    login_as(client, admin_user)
    resp = client.get("/api/reports/daily?date=2026-09-01")
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) == 1
    assert rows[0]["worker_name"] == "Amit Shah"


def test_range_report_rejects_inverted_range(client, admin_user):
    login_as(client, admin_user)
    resp = client.get("/api/reports/range?date_from=2026-09-10&date_to=2026-09-01")
    assert resp.status_code == 422


def test_monthly_report_scopes_to_month(client, supervisor_user, admin_user):
    login_as(client, supervisor_user)
    client.post("/api/attendance", json={**ROW, "attendance_date": "2026-09-15"})
    client.post("/api/attendance", json={**ROW, "attendance_date": "2026-10-01", "worker_name": "Raj Patel"})

    login_as(client, admin_user)
    resp = client.get("/api/reports/monthly?year=2026&month=9")
    rows = resp.json()
    assert len(rows) == 1
    assert rows[0]["attendance_date"] == "2026-09-15"


def test_export_csv_respects_filters(client, supervisor_user, second_supervisor_user, admin_user):
    login_as(client, supervisor_user)
    client.post("/api/attendance", json={**ROW, "worker_name": "Included Worker"})

    login_as(client, second_supervisor_user)
    client.post("/api/attendance", json={**ROW, "worker_name": "Excluded Worker"})

    login_as(client, admin_user)
    resp = client.get(f"/api/attendance/export?format=csv&supervisor_id={supervisor_user.id}")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    body = resp.text
    assert "Included Worker" in body
    assert "Excluded Worker" not in body


def test_export_excel_and_pdf_succeed(client, supervisor_user, admin_user):
    login_as(client, supervisor_user)
    client.post("/api/attendance", json=ROW)

    login_as(client, admin_user)
    excel_resp = client.get("/api/attendance/export?format=excel")
    assert excel_resp.status_code == 200
    assert len(excel_resp.content) > 0

    pdf_resp = client.get("/api/attendance/export?format=pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.content.startswith(b"%PDF")


def test_supervisor_cannot_export(client, supervisor_user):
    login_as(client, supervisor_user)
    resp = client.get("/api/attendance/export?format=csv")
    assert resp.status_code == 403

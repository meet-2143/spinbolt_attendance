from tests.conftest import login_as

VALID_ROW = {
    "attendance_date": "2026-09-01",
    "worker_name": "Amit Shah",
    "input_parts": 450,
    "total_working_hours": 8,
    "machine_stopped_time": 1,
    "attendance_status": "PRESENT",
    "remarks": "",
}


def test_create_attendance_success(client, supervisor_user):
    login_as(client, supervisor_user)
    resp = client.post("/api/attendance", json=VALID_ROW)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["worker_name"] == "Amit Shah"
    assert body["attendance_taker_name"] == supervisor_user.name
    assert body["input_parts"] == "450.00" or float(body["input_parts"]) == 450


def test_duplicate_attendance_rejected(client, supervisor_user):
    login_as(client, supervisor_user)
    first = client.post("/api/attendance", json=VALID_ROW)
    assert first.status_code == 201

    second = client.post("/api/attendance", json=VALID_ROW)
    assert second.status_code == 409
    body = second.json()
    assert body["success"] is False
    assert "already exists" in body["message"]
    assert body["existing_id"] == first.json()["id"]


def test_negative_input_parts_rejected(client, supervisor_user):
    login_as(client, supervisor_user)
    row = {**VALID_ROW, "input_parts": -5}
    resp = client.post("/api/attendance", json=row)
    assert resp.status_code == 422


def test_negative_working_hours_rejected(client, supervisor_user):
    login_as(client, supervisor_user)
    row = {**VALID_ROW, "total_working_hours": -1}
    resp = client.post("/api/attendance", json=row)
    assert resp.status_code == 422


def test_machine_stop_exceeding_hours_rejected(client, supervisor_user):
    login_as(client, supervisor_user)
    row = {**VALID_ROW, "total_working_hours": 4, "machine_stopped_time": 5}
    resp = client.post("/api/attendance", json=row)
    assert resp.status_code == 422


def test_absent_forces_zero_values_server_side(client, supervisor_user):
    login_as(client, supervisor_user)
    row = {
        **VALID_ROW,
        "attendance_status": "ABSENT",
        "input_parts": 999,
        "total_working_hours": 8,
        "machine_stopped_time": 2,
    }
    resp = client.post("/api/attendance", json=row)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert float(body["input_parts"]) == 0
    assert float(body["total_working_hours"]) == 0
    assert float(body["machine_stopped_time"]) == 0


def test_update_attendance_records_change(client, supervisor_user):
    login_as(client, supervisor_user)
    created = client.post("/api/attendance", json=VALID_ROW).json()

    resp = client.put(
        f"/api/attendance/{created['id']}",
        json={**VALID_ROW, "total_working_hours": 7, "machine_stopped_time": 2},
    )
    assert resp.status_code == 200, resp.text
    assert float(resp.json()["total_working_hours"]) == 7


def test_bulk_attendance_all_or_nothing_on_duplicate(client, supervisor_user):
    login_as(client, supervisor_user)
    # Pre-create one record that will collide with a row in the bulk payload.
    client.post("/api/attendance", json={**VALID_ROW, "worker_name": "Raj Patel"})

    resp = client.post(
        "/api/attendance/bulk",
        json={
            "rows": [
                {**VALID_ROW, "worker_name": "Jay Mehta"},
                {**VALID_ROW, "worker_name": "Raj Patel"},  # duplicate
            ]
        },
    )
    assert resp.status_code == 422
    body = resp.json()
    assert body["success"] is False
    assert len(body["errors"]) == 1
    assert body["errors"][0]["worker_name"] == "Raj Patel"

    # Transaction rolled back entirely - "Jay Mehta" must NOT have been created.
    listing = client.get("/api/attendance").json()
    names = [item["worker_name"] for item in listing["items"]]
    assert "Jay Mehta" not in names


def test_bulk_attendance_success(client, supervisor_user):
    login_as(client, supervisor_user)
    resp = client.post(
        "/api/attendance/bulk",
        json={
            "rows": [
                {**VALID_ROW, "worker_name": "Amit Shah"},
                {**VALID_ROW, "worker_name": "Raj Patel"},
            ]
        },
    )
    assert resp.status_code == 201, resp.text
    assert len(resp.json()) == 2

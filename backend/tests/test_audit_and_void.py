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


def test_create_records_audit_log(client, supervisor_user, admin_user):
    login_as(client, supervisor_user)
    created = client.post("/api/attendance", json=ROW).json()

    login_as(client, admin_user)
    resp = client.get(f"/api/audit-logs/{created['id']}")
    assert resp.status_code == 200
    logs = resp.json()
    assert len(logs) == 1
    assert logs[0]["action"] == "CREATED"
    assert logs[0]["changed_by_name"] == supervisor_user.name


def test_update_records_audit_diff(client, supervisor_user, admin_user):
    login_as(client, supervisor_user)
    created = client.post("/api/attendance", json=ROW).json()
    client.put(f"/api/attendance/{created['id']}", json={**ROW, "total_working_hours": 6})

    login_as(client, admin_user)
    logs = client.get(f"/api/audit-logs/{created['id']}").json()
    updated_logs = [log for log in logs if log["action"] == "UPDATED"]
    assert len(updated_logs) == 1
    assert updated_logs[0]["old_data"]["total_working_hours"] == 8.0
    assert updated_logs[0]["new_data"]["total_working_hours"] == 6.0
    # Unrelated fields shouldn't show up in the diff.
    assert "worker_name" not in updated_logs[0]["old_data"]


def test_supervisor_cannot_void_attendance(client, supervisor_user):
    login_as(client, supervisor_user)
    created = client.post("/api/attendance", json=ROW).json()

    resp = client.request(
        "DELETE", f"/api/attendance/{created['id']}", json={"reason": "duplicate entry"}
    )
    assert resp.status_code == 403


def test_admin_can_void_attendance(client, supervisor_user, admin_user):
    login_as(client, supervisor_user)
    created = client.post("/api/attendance", json=ROW).json()

    login_as(client, admin_user)
    resp = client.request(
        "DELETE", f"/api/attendance/{created['id']}", json={"reason": "duplicate entry"}
    )
    assert resp.status_code == 200

    # Voided records disappear from listings and direct fetch...
    get_resp = client.get(f"/api/attendance/{created['id']}")
    assert get_resp.status_code == 404

    # ...and a DELETED audit entry is recorded.
    logs = client.get(f"/api/audit-logs/{created['id']}").json()
    assert any(log["action"] == "DELETED" for log in logs)


def test_voided_worker_slot_frees_up_for_reuse(client, supervisor_user, admin_user):
    login_as(client, supervisor_user)
    created = client.post("/api/attendance", json=ROW).json()

    login_as(client, admin_user)
    client.request("DELETE", f"/api/attendance/{created['id']}", json={"reason": "wrong entry"})

    login_as(client, supervisor_user)
    resp = client.post("/api/attendance", json=ROW)
    assert resp.status_code == 201


def test_admin_dashboard_reflects_totals(client, supervisor_user, admin_user):
    login_as(client, supervisor_user)
    client.post("/api/attendance", json=ROW)

    login_as(client, admin_user)
    resp = client.get("/api/dashboard/admin")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_attendance_records"] >= 1
    assert any(row["supervisor_name"] == supervisor_user.name for row in body["supervisor_summary"])

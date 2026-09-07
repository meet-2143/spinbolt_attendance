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


def test_supervisor_cannot_access_admin_only_routes(client, supervisor_user):
    login_as(client, supervisor_user)
    resp = client.get("/api/supervisors")
    assert resp.status_code == 403


def test_admin_can_access_supervisor_management(client, admin_user):
    login_as(client, admin_user)
    resp = client.get("/api/supervisors")
    assert resp.status_code == 200


def test_supervisor_cannot_access_other_supervisors_dashboard_data(client, supervisor_user):
    login_as(client, supervisor_user)
    resp = client.get("/api/dashboard/supervisor")
    assert resp.status_code == 200


def test_admin_cannot_call_supervisor_only_dashboard(client, admin_user):
    login_as(client, admin_user)
    resp = client.get("/api/dashboard/supervisor")
    assert resp.status_code == 403


def test_supervisor_cannot_view_another_supervisors_attendance_record(client, supervisor_user, second_supervisor_user):
    login_as(client, supervisor_user)
    created = client.post("/api/attendance", json=ROW).json()

    # Switch session to the second supervisor and try to reach the first supervisor's record directly.
    login_as(client, second_supervisor_user)
    resp = client.get(f"/api/attendance/{created['id']}")
    assert resp.status_code == 403


def test_supervisor_cannot_edit_another_supervisors_attendance_record(client, supervisor_user, second_supervisor_user):
    login_as(client, supervisor_user)
    created = client.post("/api/attendance", json=ROW).json()

    login_as(client, second_supervisor_user)
    resp = client.put(f"/api/attendance/{created['id']}", json={**ROW, "total_working_hours": 1})
    assert resp.status_code == 403


def test_supervisor_history_only_shows_own_records(client, supervisor_user, second_supervisor_user):
    login_as(client, supervisor_user)
    client.post("/api/attendance", json={**ROW, "worker_name": "Supervisor One Worker"})

    login_as(client, second_supervisor_user)
    client.post("/api/attendance", json={**ROW, "worker_name": "Supervisor Two Worker"})

    resp = client.get("/api/attendance")
    names = [item["worker_name"] for item in resp.json()["items"]]
    assert names == ["Supervisor Two Worker"]


def test_admin_sees_all_supervisors_records(client, admin_user, supervisor_user, second_supervisor_user):
    login_as(client, supervisor_user)
    client.post("/api/attendance", json={**ROW, "worker_name": "Supervisor One Worker"})

    login_as(client, second_supervisor_user)
    client.post("/api/attendance", json={**ROW, "worker_name": "Supervisor Two Worker"})

    login_as(client, admin_user)
    resp = client.get("/api/attendance")
    names = {item["worker_name"] for item in resp.json()["items"]}
    assert {"Supervisor One Worker", "Supervisor Two Worker"}.issubset(names)

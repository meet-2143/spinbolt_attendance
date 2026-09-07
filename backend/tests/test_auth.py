def test_login_success_admin(client, admin_user):
    resp = client.post("/api/auth/login", json={"email": admin_user.email, "password": "Password123!"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["user"]["email"] == admin_user.email
    assert body["user"]["role"] == "ADMIN"
    assert "access_token" in resp.cookies


def test_login_wrong_password(client, admin_user):
    resp = client.post("/api/auth/login", json={"email": admin_user.email, "password": "wrong-password"})
    assert resp.status_code == 401
    assert resp.json() == {"success": False, "message": "Invalid email or password."}


def test_login_unknown_email(client):
    resp = client.post("/api/auth/login", json={"email": "nobody@test.dev", "password": "whatever123"})
    assert resp.status_code == 401


def test_login_inactive_supervisor_rejected(client, inactive_supervisor_user):
    resp = client.post(
        "/api/auth/login", json={"email": inactive_supervisor_user.email, "password": "Password123!"}
    )
    assert resp.status_code == 403
    assert "deactivated" in resp.json()["message"].lower()


def test_me_requires_authentication(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
    assert resp.json()["success"] is False


def test_me_returns_current_user_after_login(client, supervisor_user):
    client.post("/api/auth/login", json={"email": supervisor_user.email, "password": "Password123!"})
    resp = client.get("/api/auth/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == supervisor_user.email


def test_logout_clears_session(client, supervisor_user):
    client.post("/api/auth/login", json={"email": supervisor_user.email, "password": "Password123!"})
    assert client.get("/api/auth/me").status_code == 200

    client.post("/api/auth/logout")
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401

"""Integration tests — /auth endpoints."""
import pytest


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestLogin:
    def test_login_admin_success(self, client, seeded):
        resp = client.post("/auth/token", data={"username": "admin", "password": "admin123"})
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_login_wrong_password(self, client, seeded):
        resp = client.post("/auth/token", data={"username": "admin", "password": "wrong"})
        assert resp.status_code == 401

    def test_login_unknown_user(self, client, seeded):
        resp = client.post("/auth/token", data={"username": "nobody", "password": "x"})
        assert resp.status_code == 401

    def test_login_inactive_account(self, client, seeded):
        from app.models.entities import Account
        from tests.conftest import _TestSession

        with _TestSession() as db:
            acc = db.query(Account).filter_by(username="staff1").first()
            acc.is_active = False
            db.commit()

        resp = client.post("/auth/token", data={"username": "staff1", "password": "staff123"})
        assert resp.status_code == 403

        # Restore
        with _TestSession() as db:
            acc = db.query(Account).filter_by(username="staff1").first()
            acc.is_active = True
            db.commit()


class TestGetMe:
    def test_get_me_admin(self, client, seeded):
        resp = client.get("/auth/me", headers=_auth(seeded["admin_token"]))
        assert resp.status_code == 200
        body = resp.json()
        assert body["username"] == "admin"
        assert body["role"] == "admin"

    def test_get_me_no_token(self, client, seeded):
        resp = client.get("/auth/me")
        assert resp.status_code == 401

    def test_get_me_bad_token(self, client, seeded):
        resp = client.get("/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
        assert resp.status_code == 401


class TestChangePassword:
    def test_change_password_wrong_old(self, client, seeded):
        resp = client.post(
            "/auth/change-password",
            json={"old_password": "wrongold", "new_password": "newpass"},
            headers=_auth(seeded["admin_token"]),
        )
        assert resp.status_code == 400

    def test_change_password_success(self, client, seeded):
        resp = client.post(
            "/auth/change-password",
            json={"old_password": "admin123", "new_password": "admin123"},
            headers=_auth(seeded["admin_token"]),
        )
        assert resp.status_code == 200
        assert "message" in resp.json()

"""Integration tests — /departments endpoints."""
import pytest


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestListDepartments:
    def test_list_requires_auth(self, client, seeded):
        resp = client.get("/departments")
        assert resp.status_code == 401

    def test_list_returns_array(self, client, seeded):
        resp = client.get("/departments", headers=_auth(seeded["staff_token"]))
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_search_filter(self, client, seeded):
        resp = client.get("/departments?search=TEST", headers=_auth(seeded["admin_token"]))
        assert resp.status_code == 200
        names = [d["code"] for d in resp.json()]
        assert "TEST" in names


class TestCreateDepartment:
    def test_admin_can_create(self, client, seeded):
        resp = client.post(
            "/departments",
            json={"code": "NEW01", "name": "Khoa Moi 01", "description": "desc"},
            headers=_auth(seeded["admin_token"]),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == "NEW01"
        assert body["lecturer_count"] == 0

    def test_staff_cannot_create(self, client, seeded):
        resp = client.post(
            "/departments",
            json={"code": "NEW02", "name": "Khoa Moi 02"},
            headers=_auth(seeded["staff_token"]),
        )
        assert resp.status_code == 403


class TestGetDepartment:
    def test_get_existing(self, client, seeded):
        # Grab first dept from list
        lst = client.get("/departments", headers=_auth(seeded["admin_token"])).json()
        dep_id = lst[0]["id"]
        resp = client.get(f"/departments/{dep_id}", headers=_auth(seeded["admin_token"]))
        assert resp.status_code == 200
        assert resp.json()["id"] == dep_id

    def test_get_nonexistent(self, client, seeded):
        resp = client.get("/departments/999999", headers=_auth(seeded["admin_token"]))
        assert resp.status_code == 404


class TestUpdateDepartment:
    def test_update_name(self, client, seeded):
        created = client.post(
            "/departments",
            json={"code": "UPD01", "name": "Before Update"},
            headers=_auth(seeded["admin_token"]),
        ).json()
        resp = client.put(
            f"/departments/{created['id']}",
            json={"name": "After Update"},
            headers=_auth(seeded["admin_token"]),
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "After Update"


class TestDeleteDepartment:
    def test_delete_empty_department(self, client, seeded):
        created = client.post(
            "/departments",
            json={"code": "DEL01", "name": "To Delete"},
            headers=_auth(seeded["admin_token"]),
        ).json()
        resp = client.delete(f"/departments/{created['id']}", headers=_auth(seeded["admin_token"]))
        assert resp.status_code == 200

        # Soft-deleted: should return 404 on subsequent GET
        get_resp = client.get(f"/departments/{created['id']}", headers=_auth(seeded["admin_token"]))
        assert get_resp.status_code == 404

    def test_delete_department_with_lecturers_returns_409(self, client, seeded):
        # "TEST" dept created in conftest has one lecturer
        lst = client.get("/departments?search=TEST", headers=_auth(seeded["admin_token"])).json()
        assert lst, "TEST department not found"
        dep_id = lst[0]["id"]
        resp = client.delete(f"/departments/{dep_id}", headers=_auth(seeded["admin_token"]))
        assert resp.status_code == 409

    def test_delete_nonexistent(self, client, seeded):
        resp = client.delete("/departments/999999", headers=_auth(seeded["admin_token"]))
        assert resp.status_code == 404

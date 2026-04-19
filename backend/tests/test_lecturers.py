"""Integration tests — /lecturers endpoints (soft delete included)."""
import pytest


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _get_test_dept_id(client, token) -> int:
    lst = client.get("/departments?search=TEST", headers=_auth(token)).json()
    assert lst, "TEST department not seeded"
    return lst[0]["id"]


def _new_lecturer(dept_id: int, suffix: str) -> dict:
    return {
        "employee_code": f"GV_T_{suffix}",
        "full_name": f"Test Lecturer {suffix}",
        "email": f"lec_{suffix}@eaut.edu.vn",
        "phone": "0900000099",
        "gender": "female",
        "date_of_birth": "1990-06-15",
        "degree": "ThS",
        "position": "Giang vien",
        "department_id": dept_id,
        "hire_date": "2020-09-01",
        "status": "active",
    }


class TestListLecturers:
    def test_requires_auth(self, client, seeded):
        resp = client.get("/lecturers")
        assert resp.status_code == 401

    def test_returns_paginated(self, client, seeded):
        resp = client.get("/lecturers", headers=_auth(seeded["staff_token"]))
        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body and "total" in body

    def test_search(self, client, seeded):
        resp = client.get("/lecturers?search=Nguyen Test", headers=_auth(seeded["admin_token"]))
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert any("Nguyen Test" in i["full_name"] for i in items)


class TestCreateLecturer:
    def test_admin_can_create(self, client, seeded):
        dept_id = _get_test_dept_id(client, seeded["admin_token"])
        resp = client.post(
            "/lecturers",
            json=_new_lecturer(dept_id, "CRE01"),
            headers=_auth(seeded["admin_token"]),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["employee_code"] == "GV_T_CRE01"
        assert body["department"]["code"] == "TEST"

    def test_staff_cannot_create(self, client, seeded):
        dept_id = _get_test_dept_id(client, seeded["staff_token"])
        resp = client.post(
            "/lecturers",
            json=_new_lecturer(dept_id, "CRE02"),
            headers=_auth(seeded["staff_token"]),
        )
        assert resp.status_code == 403


class TestGetLecturer:
    def test_get_existing(self, client, seeded):
        # Use the seeded lecturer
        items = client.get("/lecturers?search=Nguyen Test", headers=_auth(seeded["admin_token"])).json()["items"]
        lec_id = items[0]["id"]
        resp = client.get(f"/lecturers/{lec_id}", headers=_auth(seeded["admin_token"]))
        assert resp.status_code == 200
        assert resp.json()["id"] == lec_id

    def test_get_nonexistent(self, client, seeded):
        resp = client.get("/lecturers/999999", headers=_auth(seeded["admin_token"]))
        assert resp.status_code == 404


class TestUpdateLecturer:
    def test_update_status(self, client, seeded):
        dept_id = _get_test_dept_id(client, seeded["admin_token"])
        created = client.post(
            "/lecturers",
            json=_new_lecturer(dept_id, "UPD01"),
            headers=_auth(seeded["admin_token"]),
        ).json()
        resp = client.put(
            f"/lecturers/{created['id']}",
            json={"status": "on_leave"},
            headers=_auth(seeded["admin_token"]),
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "on_leave"


class TestSoftDeleteLecturer:
    def test_delete_removes_from_list(self, client, seeded):
        dept_id = _get_test_dept_id(client, seeded["admin_token"])
        created = client.post(
            "/lecturers",
            json=_new_lecturer(dept_id, "DEL01"),
            headers=_auth(seeded["admin_token"]),
        ).json()
        lec_id = created["id"]

        del_resp = client.delete(f"/lecturers/{lec_id}", headers=_auth(seeded["admin_token"]))
        assert del_resp.status_code == 200

        # Soft-deleted: GET should return 404
        get_resp = client.get(f"/lecturers/{lec_id}", headers=_auth(seeded["admin_token"]))
        assert get_resp.status_code == 404

        # Should not appear in list
        search = client.get(
            f"/lecturers?search={created['employee_code']}",
            headers=_auth(seeded["admin_token"]),
        ).json()
        codes = [i["employee_code"] for i in search["items"]]
        assert created["employee_code"] not in codes

    def test_delete_nonexistent(self, client, seeded):
        resp = client.delete("/lecturers/999999", headers=_auth(seeded["admin_token"]))
        assert resp.status_code == 404

    def test_staff_cannot_delete(self, client, seeded):
        items = client.get("/lecturers", headers=_auth(seeded["admin_token"])).json()["items"]
        lec_id = items[0]["id"]
        resp = client.delete(f"/lecturers/{lec_id}", headers=_auth(seeded["staff_token"]))
        assert resp.status_code == 403

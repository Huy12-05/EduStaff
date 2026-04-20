# api/lecturer_api.py - Lecturer CRUD endpoints

from urllib.parse import urlencode

import api.client as client


def get_lecturers(
    page: int = 1,
    size: int = 20,
    search: str = "",
    department_id: int = None,
    degree: str = "",
    position: str = "",
    gender: str = "",
    status: str = "",
) -> dict:
    params: dict = {"page": page, "size": size}
    if search:
        params["search"] = search
    if department_id:
        params["department_id"] = department_id
    if degree:
        params["degree"] = degree
    if position:
        params["position"] = position
    if gender:
        params["gender"] = gender
    if status:
        params["status"] = status
    return client.get("/lecturers", params=params)


def get_lecturer(lecturer_id: int) -> dict:
    return client.get(f"/lecturers/{lecturer_id}")


def create_lecturer(data: dict) -> dict:
    return client.post("/lecturers", json=data)


def update_lecturer(lecturer_id: int, data: dict) -> dict:
    return client.put(f"/lecturers/{lecturer_id}", json=data)


def delete_lecturer(lecturer_id: int):
    return client.delete(f"/lecturers/{lecturer_id}")


def upload_avatar(lecturer_id: int, file_bytes: bytes, filename: str) -> dict:
    return client.post_file(f"/lecturers/{lecturer_id}/avatar", filename, file_bytes)


def export_excel(
    search: str = "",
    department_id: int = None,
    degree: str = "",
    position: str = "",
    gender: str = "",
    status: str = "",
) -> bytes:
    params = {
        "search": search,
        "degree": degree,
        "position": position,
        "gender": gender,
        "status": status,
    }
    if department_id:
        params["department_id"] = department_id
    params = {k: v for k, v in params.items() if v is not None and v != ""}
    qs = urlencode(params)
    return client.get_file(f"/lecturers/export{'?' + qs if qs else ''}")


def export_pdf(
    search: str = "",
    department_id: int = None,
    degree: str = "",
    position: str = "",
    gender: str = "",
    status: str = "",
) -> bytes:
    params = {
        "search": search,
        "degree": degree,
        "position": position,
        "gender": gender,
        "status": status,
    }
    if department_id:
        params["department_id"] = department_id
    params = {k: v for k, v in params.items() if v is not None and v != ""}
    qs = urlencode(params)
    return client.get_file(f"/lecturers/export/pdf{'?' + qs if qs else ''}")

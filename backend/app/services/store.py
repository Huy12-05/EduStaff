from datetime import date, datetime, time

from sqlalchemy import delete, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.entities import Account, AuditLog, Department, Lecturer, Schedule


def _to_iso(value: datetime | date | time | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat(timespec="seconds")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, time):
        return value.strftime("%H:%M")
    return str(value)


def _parse_date(raw: str | date | None) -> date | None:
    if raw is None or raw == "":
        return None
    if isinstance(raw, date):
        return raw
    return date.fromisoformat(str(raw))


def _parse_time(raw: str | time | None) -> time | None:
    if raw is None or raw == "":
        return None
    if isinstance(raw, time):
        return raw
    return time.fromisoformat(str(raw))


class DatabaseStore:
    """Store su dung SQLAlchemy/MySQL nhung giu nguyen contract cho routers."""

    @staticmethod
    def _paginate_items(items: list[dict], total: int, page: int, size: int) -> dict:
        pages = max(1, (total + size - 1) // size)
        page = max(1, min(page, pages))
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages,
        }

    @staticmethod
    def _map_account(account: Account, include_password_hash: bool = False) -> dict:
        row = {
            "id": account.id,
            "username": account.username,
            "full_name": account.full_name,
            "role": account.role,
            "is_active": account.is_active,
            "created_at": _to_iso(account.created_at),
        }
        if include_password_hash:
            row["password_hash"] = account.password_hash
        return row

    @staticmethod
    def _map_department(dep: Department, lecturer_count: int = 0) -> dict:
        return {
            "id": dep.id,
            "code": dep.code,
            "name": dep.name,
            "description": dep.description,
            "lecturer_count": lecturer_count,
        }

    @staticmethod
    def _map_lecturer(lecturer: Lecturer) -> dict:
        department = None
        if lecturer.department:
            department = {
                "id": lecturer.department.id,
                "code": lecturer.department.code,
                "name": lecturer.department.name,
                "description": lecturer.department.description,
            }

        return {
            "id": lecturer.id,
            "employee_code": lecturer.employee_code,
            "full_name": lecturer.full_name,
            "email": lecturer.email,
            "phone": lecturer.phone,
            "gender": lecturer.gender,
            "date_of_birth": _to_iso(lecturer.date_of_birth),
            "degree": lecturer.degree,
            "position": lecturer.position,
            "department_id": lecturer.department_id,
            "hire_date": _to_iso(lecturer.hire_date),
            "status": lecturer.status,
            "department": department,
        }

    def _map_schedule(self, schedule: Schedule) -> dict:
        lecturer = self._map_lecturer(schedule.lecturer) if schedule.lecturer else None
        return {
            "id": schedule.id,
            "lecturer_id": schedule.lecturer_id,
            "subject_name": schedule.subject_name,
            "subject_code": schedule.subject_code,
            "room": schedule.room,
            "day_of_week": schedule.day_of_week,
            "start_time": _to_iso(schedule.start_time),
            "end_time": _to_iso(schedule.end_time),
            "semester": schedule.semester,
            "academic_year": schedule.academic_year,
            "lecturer": lecturer,
        }

    @staticmethod
    def _map_audit(log: AuditLog) -> dict:
        return {
            "id": log.id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "details": log.details,
            "username": log.username,
            "ip_address": log.ip_address,
            "created_at": _to_iso(log.created_at),
        }

    def seed_initial_data(self) -> None:
        """Seed du lieu mau idempotent de frontend co data khi khoi dong lan dau."""
        with SessionLocal() as db:
            has_account = db.scalar(select(func.count(Account.id))) or 0
            if has_account > 0:
                return

            admin = Account(
                username="admin",
                full_name="Quan tri vien",
                role="admin",
                is_active=True,
                password_hash=hash_password("admin123"),
            )
            staff = Account(
                username="staff",
                full_name="Nhan su",
                role="staff",
                is_active=True,
                password_hash=hash_password("staff123"),
            )
            db.add_all([admin, staff])

            dep_cntt = Department(code="CNTT", name="Cong nghe Thong tin", description="Khoa CNTT")
            dep_dtvt = Department(code="DTVT", name="Dien tu Vien thong", description="Khoa DTVT")
            dep_qtkd = Department(code="QTKD", name="Quan tri Kinh doanh", description="Khoa QTKD")
            db.add_all([dep_cntt, dep_dtvt, dep_qtkd])
            db.flush()

            lec_1 = Lecturer(
                employee_code="GV001",
                full_name="Nguyen Van A",
                email="a@university.edu.vn",
                phone="0901000001",
                gender="male",
                date_of_birth=date(1980, 1, 1),
                degree="TS",
                position="Giang vien chinh",
                department_id=dep_cntt.id,
                hire_date=date(2010, 9, 1),
                status="active",
            )
            lec_2 = Lecturer(
                employee_code="GV002",
                full_name="Tran Thi B",
                email="b@university.edu.vn",
                phone="0901000002",
                gender="female",
                date_of_birth=date(1985, 3, 10),
                degree="ThS",
                position="Giang vien",
                department_id=dep_dtvt.id,
                hire_date=date(2014, 9, 1),
                status="active",
            )
            db.add_all([lec_1, lec_2])
            db.flush()

            schedule = Schedule(
                lecturer_id=lec_1.id,
                subject_name="Lap trinh Python",
                subject_code="CS101",
                room="A101",
                day_of_week="Mon",
                start_time=time(8, 0),
                end_time=time(10, 0),
                semester="HK1",
                academic_year="2026",
            )
            db.add(schedule)
            db.commit()

    def find_account_by_username(self, username: str) -> dict | None:
        with SessionLocal() as db:
            account = db.scalar(select(Account).where(Account.username == username))
            if not account:
                return None
            return self._map_account(account, include_password_hash=True)

    def list_accounts(self, search: str = "", role: str = "", is_active: bool | None = None) -> list[dict]:
        with SessionLocal() as db:
            query = select(Account)
            if search:
                keyword = f"%{search}%"
                query = query.where(or_(Account.username.ilike(keyword), Account.full_name.ilike(keyword)))
            if role:
                query = query.where(Account.role == role)
            if is_active is not None:
                query = query.where(Account.is_active.is_(is_active))
            query = query.order_by(Account.id.asc())
            rows = db.scalars(query).all()
            return [self._map_account(row) for row in rows]

    def get_account(self, account_id: int) -> dict | None:
        with SessionLocal() as db:
            account = db.get(Account, account_id)
            if not account:
                return None
            return self._map_account(account)

    def create_account(self, data: dict) -> dict:
        with SessionLocal() as db:
            account = Account(
                username=data["username"],
                full_name=data["full_name"],
                role=data.get("role", "staff"),
                is_active=True,
                password_hash=hash_password(data["password"]),
            )
            db.add(account)
            db.commit()
            db.refresh(account)
            return self._map_account(account)

    def update_account(self, account_id: int, data: dict) -> dict | None:
        with SessionLocal() as db:
            account = db.get(Account, account_id)
            if not account:
                return None

            if data.get("full_name") is not None:
                account.full_name = data["full_name"]
            if data.get("role") is not None:
                account.role = data["role"]
            if data.get("password"):
                account.password_hash = hash_password(data["password"])

            db.commit()
            db.refresh(account)
            return self._map_account(account)

    def delete_account(self, account_id: int) -> bool:
        with SessionLocal() as db:
            account = db.get(Account, account_id)
            if not account:
                return False
            db.delete(account)
            db.commit()
            return True

    def toggle_account(self, account_id: int) -> dict | None:
        with SessionLocal() as db:
            account = db.get(Account, account_id)
            if not account:
                return None
            account.is_active = not account.is_active
            db.commit()
            db.refresh(account)
            return self._map_account(account)

    def reset_password(self, account_id: int, new_password: str) -> dict | None:
        with SessionLocal() as db:
            account = db.get(Account, account_id)
            if not account:
                return None
            account.password_hash = hash_password(new_password)
            db.commit()
            db.refresh(account)
            return self._map_account(account)

    def change_password(self, username: str, new_password: str) -> None:
        with SessionLocal() as db:
            account = db.scalar(select(Account).where(Account.username == username))
            if account:
                account.password_hash = hash_password(new_password)
                db.commit()

    def list_departments(self, search: str = "") -> list[dict]:
        with SessionLocal() as db:
            query = select(Department).where(Department.is_deleted.is_(False))
            if search:
                keyword = f"%{search}%"
                query = query.where(or_(Department.code.ilike(keyword), Department.name.ilike(keyword)))
            query = query.order_by(Department.id.asc())

            departments = db.scalars(query).all()
            results: list[dict] = []
            for dep in departments:
                lecturer_count = db.scalar(
                    select(func.count(Lecturer.id)).where(
                        (Lecturer.department_id == dep.id) & (Lecturer.is_deleted.is_(False))
                    )
                ) or 0
                results.append(self._map_department(dep, lecturer_count=lecturer_count))
            return results

    def get_department(self, department_id: int) -> dict | None:
        with SessionLocal() as db:
            dep = db.get(Department, department_id)
            if not dep or dep.is_deleted:
                return None
            lecturer_count = db.scalar(
                select(func.count(Lecturer.id)).where(
                    (Lecturer.department_id == dep.id) & (Lecturer.is_deleted.is_(False))
                )
            ) or 0
            return self._map_department(dep, lecturer_count=lecturer_count)

    def create_department(self, data: dict) -> dict:
        with SessionLocal() as db:
            dep = Department(
                code=data["code"],
                name=data["name"],
                description=data.get("description"),
            )
            db.add(dep)
            db.commit()
            db.refresh(dep)
            return self._map_department(dep, lecturer_count=0)

    def update_department(self, department_id: int, data: dict) -> dict | None:
        with SessionLocal() as db:
            dep = db.get(Department, department_id)
            if not dep:
                return None

            if data.get("code") is not None:
                dep.code = data["code"]
            if data.get("name") is not None:
                dep.name = data["name"]
            if "description" in data:
                dep.description = data.get("description")

            db.commit()
            db.refresh(dep)
            lecturer_count = db.scalar(
                select(func.count(Lecturer.id)).where(Lecturer.department_id == dep.id)
            ) or 0
            return self._map_department(dep, lecturer_count=lecturer_count)

    def delete_department(self, department_id: int) -> bool:
        with SessionLocal() as db:
            dep = db.get(Department, department_id)
            if not dep or dep.is_deleted:
                return False
            active_count = db.scalar(
                select(func.count(Lecturer.id)).where(
                    (Lecturer.department_id == department_id) & (Lecturer.is_deleted.is_(False))
                )
            ) or 0
            if active_count > 0:
                raise ValueError(f"Khoa dang co {active_count} giang vien. Chuyen giang vien truoc khi xoa khoa.")
            dep.is_deleted = True
            db.commit()
            return True

    def list_lecturers(
        self,
        page: int,
        size: int,
        search: str = "",
        department_id: int | None = None,
        degree: str = "",
        position: str = "",
        gender: str = "",
        status: str = "",
    ) -> dict:
        with SessionLocal() as db:
            query = select(Lecturer).options(joinedload(Lecturer.department)).where(Lecturer.is_deleted.is_(False))

            if search:
                keyword = f"%{search}%"
                query = query.where(
                    or_(
                        Lecturer.employee_code.ilike(keyword),
                        Lecturer.full_name.ilike(keyword),
                        Lecturer.email.ilike(keyword),
                    )
                )
            if department_id:
                query = query.where(Lecturer.department_id == department_id)
            if degree:
                query = query.where(Lecturer.degree == degree)
            if position:
                query = query.where(Lecturer.position == position)
            if gender:
                query = query.where(Lecturer.gender == gender)
            if status:
                query = query.where(Lecturer.status == status)

            total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
            pages = max(1, (total + size - 1) // size)
            page = max(1, min(page, pages))

            rows = db.scalars(
                query.order_by(Lecturer.id.asc()).offset((page - 1) * size).limit(size)
            ).all()

            mapped = [self._map_lecturer(row) for row in rows]
            return self._paginate_items(mapped, total=total, page=page, size=size)

    def get_lecturer(self, lecturer_id: int) -> dict | None:
        with SessionLocal() as db:
            query = (
                select(Lecturer)
                .options(joinedload(Lecturer.department))
                .where((Lecturer.id == lecturer_id) & (Lecturer.is_deleted.is_(False)))
            )
            lecturer = db.scalar(query)
            if not lecturer:
                return None
            return self._map_lecturer(lecturer)

    def create_lecturer(self, data: dict) -> dict:
        with SessionLocal() as db:
            lecturer = Lecturer(
                employee_code=data["employee_code"],
                full_name=data["full_name"],
                email=data["email"],
                phone=data.get("phone"),
                gender=data["gender"],
                date_of_birth=_parse_date(data.get("date_of_birth")),
                degree=data["degree"],
                position=data.get("position"),
                department_id=data["department_id"],
                hire_date=_parse_date(data.get("hire_date")),
                status=data["status"],
            )
            db.add(lecturer)
            try:
                db.commit()
            except IntegrityError as exc:
                db.rollback()
                msg = str(exc.orig)
                if "employee_code" in msg:
                    raise ValueError(f"Mã giảng viên '{data['employee_code']}' đã tồn tại.")
                if "email" in msg:
                    raise ValueError(f"Email '{data['email']}' đã được sử dụng.")
                raise ValueError("Dữ liệu bị trùng lặp, vui lòng kiểm tra lại.")
            db.refresh(lecturer)
            lecturer = db.scalar(
                select(Lecturer)
                .options(joinedload(Lecturer.department))
                .where(Lecturer.id == lecturer.id)
            )
            return self._map_lecturer(lecturer)

    def update_lecturer(self, lecturer_id: int, data: dict) -> dict | None:
        with SessionLocal() as db:
            lecturer = db.get(Lecturer, lecturer_id)
            if not lecturer:
                return None

            for field in ("employee_code", "full_name", "email", "phone", "gender", "degree", "position", "status"):
                if data.get(field) is not None:
                    setattr(lecturer, field, data[field])

            if data.get("department_id") is not None:
                lecturer.department_id = data["department_id"]
            if data.get("date_of_birth") is not None:
                lecturer.date_of_birth = _parse_date(data["date_of_birth"])
            if data.get("hire_date") is not None:
                lecturer.hire_date = _parse_date(data["hire_date"])

            try:
                db.commit()
            except IntegrityError as exc:
                db.rollback()
                msg = str(exc.orig)
                if "employee_code" in msg:
                    raise ValueError(f"Mã giảng viên đã tồn tại.")
                if "email" in msg:
                    raise ValueError(f"Email đã được sử dụng.")
                raise ValueError("Dữ liệu bị trùng lặp, vui lòng kiểm tra lại.")
            lecturer = db.scalar(
                select(Lecturer)
                .options(joinedload(Lecturer.department))
                .where(Lecturer.id == lecturer_id)
            )
            return self._map_lecturer(lecturer)

    def delete_lecturer(self, lecturer_id: int) -> bool:
        with SessionLocal() as db:
            lecturer = db.get(Lecturer, lecturer_id)
            if not lecturer or lecturer.is_deleted:
                return False
            lecturer.is_deleted = True
            db.commit()
            return True

    def list_schedules(
        self,
        page: int,
        size: int,
        lecturer_id: int | None = None,
        day_of_week: str = "",
        semester: str = "",
        academic_year: str = "",
    ) -> dict:
        with SessionLocal() as db:
            query = select(Schedule).options(
                joinedload(Schedule.lecturer).joinedload(Lecturer.department)
            )

            if lecturer_id:
                query = query.where(Schedule.lecturer_id == lecturer_id)
            if day_of_week:
                query = query.where(Schedule.day_of_week == day_of_week)
            if semester:
                query = query.where(Schedule.semester == semester)
            if academic_year:
                query = query.where(Schedule.academic_year == str(academic_year))

            total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
            pages = max(1, (total + size - 1) // size)
            page = max(1, min(page, pages))

            rows = db.scalars(
                query.order_by(Schedule.id.asc()).offset((page - 1) * size).limit(size)
            ).all()
            mapped = [self._map_schedule(row) for row in rows]
            return self._paginate_items(mapped, total=total, page=page, size=size)

    def get_schedule(self, schedule_id: int) -> dict | None:
        with SessionLocal() as db:
            row = db.scalar(
                select(Schedule)
                .options(joinedload(Schedule.lecturer).joinedload(Lecturer.department))
                .where(Schedule.id == schedule_id)
            )
            if not row:
                return None
            return self._map_schedule(row)

    def create_schedule(self, data: dict) -> dict:
        with SessionLocal() as db:
            row = Schedule(
                lecturer_id=data["lecturer_id"],
                subject_name=data["subject_name"],
                subject_code=data["subject_code"],
                room=data["room"],
                day_of_week=data["day_of_week"],
                start_time=_parse_time(data.get("start_time")),
                end_time=_parse_time(data.get("end_time")),
                semester=data["semester"],
                academic_year=str(data["academic_year"]),
            )
            db.add(row)
            db.commit()
            row = db.scalar(
                select(Schedule)
                .options(joinedload(Schedule.lecturer).joinedload(Lecturer.department))
                .where(Schedule.id == row.id)
            )
            return self._map_schedule(row)

    def update_schedule(self, schedule_id: int, data: dict) -> dict | None:
        with SessionLocal() as db:
            row = db.get(Schedule, schedule_id)
            if not row:
                return None

            for field in ("lecturer_id", "subject_name", "subject_code", "room", "day_of_week", "semester"):
                if data.get(field) is not None:
                    setattr(row, field, data[field])

            if data.get("start_time") is not None:
                row.start_time = _parse_time(data["start_time"])
            if data.get("end_time") is not None:
                row.end_time = _parse_time(data["end_time"])
            if data.get("academic_year") is not None:
                row.academic_year = str(data["academic_year"])

            db.commit()
            row = db.scalar(
                select(Schedule)
                .options(joinedload(Schedule.lecturer).joinedload(Lecturer.department))
                .where(Schedule.id == schedule_id)
            )
            return self._map_schedule(row)

    def delete_schedule(self, schedule_id: int) -> bool:
        with SessionLocal() as db:
            row = db.get(Schedule, schedule_id)
            if not row:
                return False
            db.delete(row)
            db.commit()
            return True

    def add_audit_log(self, row: dict) -> None:
        with SessionLocal() as db:
            created_at = row.get("created_at")
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)
            if not isinstance(created_at, datetime):
                created_at = datetime.utcnow()

            log = AuditLog(
                action=row.get("action", "unknown"),
                entity_type=row.get("entity_type", "system"),
                entity_id=row.get("entity_id"),
                details=row.get("details"),
                username=row.get("username", "system"),
                ip_address=row.get("ip_address"),
                created_at=created_at,
            )
            db.add(log)
            db.commit()

    def list_audit_logs(
        self,
        page: int,
        size: int,
        action: str = "",
        entity_type: str = "",
        username: str = "",
        date_from: str = "",
        date_to: str = "",
    ) -> dict:
        with SessionLocal() as db:
            query = select(AuditLog)
            if action:
                query = query.where(AuditLog.action == action)
            if entity_type:
                query = query.where(AuditLog.entity_type == entity_type)
            if username:
                query = query.where(AuditLog.username.ilike(f"%{username}%"))
            if date_from:
                query = query.where(AuditLog.created_at >= datetime.fromisoformat(f"{date_from}T00:00:00"))
            if date_to:
                query = query.where(AuditLog.created_at <= datetime.fromisoformat(f"{date_to}T23:59:59"))

            total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
            pages = max(1, (total + size - 1) // size)
            page = max(1, min(page, pages))

            rows = db.scalars(
                query.order_by(AuditLog.id.desc()).offset((page - 1) * size).limit(size)
            ).all()
            mapped = [self._map_audit(row) for row in rows]
            return self._paginate_items(mapped, total=total, page=page, size=size)

    def overview_stats(self) -> dict:
        with SessionLocal() as db:
            return {
                "total_lecturers": db.scalar(select(func.count(Lecturer.id))) or 0,
                "total_departments": db.scalar(select(func.count(Department.id))) or 0,
                "total_schedules": db.scalar(select(func.count(Schedule.id))) or 0,
                "total_accounts": db.scalar(select(func.count(Account.id))) or 0,
            }

    def stats_by_department(self) -> list[dict]:
        with SessionLocal() as db:
            query = (
                select(Department.code, Department.name, func.count(Lecturer.id))
                .select_from(Department)
                .outerjoin(
                    Lecturer,
                    (Lecturer.department_id == Department.id) & (Lecturer.is_deleted.is_(False)),
                )
                .where(Department.is_deleted.is_(False))
                .group_by(Department.id, Department.code, Department.name)
                .order_by(Department.id.asc())
            )
            rows = db.execute(query).all()
            return [
                {
                    "department_name": row[1],
                    "department_code": row[0],
                    "count": row[2],
                }
                for row in rows
            ]

    def stats_by_degree(self) -> list[dict]:
        with SessionLocal() as db:
            rows = db.execute(
                select(Lecturer.degree, func.count(Lecturer.id))
                .group_by(Lecturer.degree)
                .order_by(Lecturer.degree.asc())
            ).all()
            return [{"degree": row[0] or "Khac", "count": row[1]} for row in rows]

    def stats_by_position(self) -> list[dict]:
        with SessionLocal() as db:
            rows = db.execute(
                select(Lecturer.position, func.count(Lecturer.id))
                .group_by(Lecturer.position)
                .order_by(Lecturer.position.asc())
            ).all()
            return [{"position": row[0] or "Khong xac dinh", "count": row[1]} for row in rows]


STORE = DatabaseStore()

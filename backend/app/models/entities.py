from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="staff")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")

    lecturers: Mapped[list["Lecturer"]] = relationship(back_populates="department")


class Lecturer(Base):
    __tablename__ = "lecturers"
    __table_args__ = (
        # Most queries filter by is_deleted first, then status or department
        Index("ix_lecturers_deleted_status",   "is_deleted", "status"),
        Index("ix_lecturers_deleted_dept",     "is_deleted", "department_id"),
        Index("ix_lecturers_deleted_degree",   "is_deleted", "degree"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    gender: Mapped[str] = mapped_column(String(20))
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    degree: Mapped[str] = mapped_column(String(50))
    position: Mapped[str | None] = mapped_column(String(100), nullable=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True)
    hire_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")

    department: Mapped[Department] = relationship(back_populates="lecturers")
    schedules: Mapped[list["Schedule"]] = relationship(back_populates="lecturer")


class Schedule(Base):
    __tablename__ = "schedules"
    __table_args__ = (
        # Common filter pair: semester + academic_year
        Index("ix_schedules_semester_year", "semester", "academic_year"),
        # Filter by lecturer within a semester
        Index("ix_schedules_lecturer_semester", "lecturer_id", "semester"),
        # Slot lookup: start_time + end_time
        Index("ix_schedules_time_slot", "start_time", "end_time"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lecturer_id: Mapped[int] = mapped_column(ForeignKey("lecturers.id"), index=True)
    subject_name: Mapped[str] = mapped_column(String(255))
    subject_code: Mapped[str] = mapped_column(String(50), index=True)
    room: Mapped[str] = mapped_column(String(50))
    day_of_week: Mapped[str] = mapped_column(String(10), index=True)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    semester: Mapped[str] = mapped_column(String(20), index=True)
    academic_year: Mapped[str] = mapped_column(String(20), index=True)

    lecturer: Mapped[Lecturer] = relationship(back_populates="schedules")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        # Dashboard/filter: created_at descending is the most common query pattern
        Index("ix_audit_logs_created_desc", "created_at"),
        Index("ix_audit_logs_username_action", "username", "action"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    action: Mapped[str] = mapped_column(String(50), index=True)
    entity_type: Mapped[str] = mapped_column(String(50), index=True)
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    username: Mapped[str] = mapped_column(String(100), index=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

# components/badges.py - Pill-shaped status badges

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

_PRESETS: dict[str, tuple[str, str]] = {
    "active": ("#1A3A2A", "#3FB950"),
    "inactive": ("#2D1F1F", "#F85149"),
    "on_leave": ("#3A2A0A", "#D29922"),
    "admin": ("#1A2A4A", "#388BFD"),
    "staff": ("#2A1A3A", "#BC8CFF"),
    "success": ("#1A3A2A", "#3FB950"),
    "error": ("#3D1318", "#F85149"),
    "warning": ("#3A2A0A", "#D29922"),
    "pending": ("#3A2A0A", "#D29922"),
    "info": ("#0D2349", "#58A6FF"),
    "login": ("#0D2349", "#58A6FF"),
    "create": ("#1A3A2A", "#3FB950"),
    "update": ("#3A2A0A", "#D29922"),
    "delete": ("#3D1318", "#F85149"),
    "blue": ("#1A2A4A", "#388BFD"),
    "green": ("#1A3A2A", "#3FB950"),
    "red": ("#3D1318", "#F85149"),
    "yellow": ("#3A2A0A", "#D29922"),
    "purple": ("#2A1A3A", "#BC8CFF"),
    "gray": ("#21262D", "#8B949E"),
}


class Badge(QLabel):
    """Pill-shaped coloured badge."""

    def __init__(self, text: str, preset: str = "gray",
                 bg: str = "", fg: str = "", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if bg and fg:
            background, foreground = bg, fg
        else:
            background, foreground = _PRESETS.get(preset, _PRESETS["gray"])
        self.setStyleSheet(
            f"background:{background}; color:{foreground};"
            "border-radius:10px; padding:2px 10px;"
            "font-size:11px; font-weight:600; letter-spacing:0.3px;"
        )

    @staticmethod
    def status(value: str) -> "Badge":
        mapping = {
            "active":   ("Đang dạy",  "active"),
            "inactive": ("Nghỉ việc", "inactive"),
            "on_leave": ("Tạm nghỉ",  "on_leave"),
        }
        label, preset = mapping.get(value, (value or "-", "gray"))
        return Badge(label, preset)

    @staticmethod
    def degree(value: str) -> "Badge":
        mapping = {"GS": "blue", "PGS": "purple", "TS": "info", "ThS": "green"}
        return Badge(value or "-", mapping.get(value, "gray"))

    @staticmethod
    def role(value: str) -> "Badge":
        mapping = {"admin": ("Quản trị", "admin"), "staff": ("Nhân viên", "staff")}
        label, preset = mapping.get(value, (value or "-", "gray"))
        return Badge(label, preset)

    @staticmethod
    def account_status(is_active) -> "Badge":
        return Badge("Hoạt động", "active") if is_active else Badge("Bị khóa", "inactive")

    @staticmethod
    def action(value: str) -> "Badge":
        mapping = {
            "login":  ("Đăng nhập", "login"),
            "create": ("Tạo mới",   "create"),
            "update": ("Cập nhật",  "update"),
            "delete": ("Xóa",       "delete"),
        }
        label, preset = mapping.get(value, (value or "-", "gray"))
        return Badge(label, preset)

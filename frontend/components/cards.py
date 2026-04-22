# components/cards.py — Stat card + header card helpers

from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from qfluentwidgets import ElevatedCardWidget, BodyLabel, CaptionLabel, IconWidget, FluentIcon
from ui.icon_manager import IconManager


def _apply_soft_shadow(widget: QWidget):
    # Shadow nhẹ đúng tinh thần Fluent, tránh quá đậm để giữ độ thoáng.
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(24)
    shadow.setXOffset(0)
    shadow.setYOffset(4)
    shadow.setColor(QColor(0, 0, 0, 70))
    widget.setGraphicsEffect(shadow)


class StatCard(ElevatedCardWidget):
    """
    Dashboard stat card:
      ┌────────────────────────────────────┐
      │  [●icon bubble]      [══ bar]      │
      │  1 234                             │
      │  Tổng Giảng Viên                  │
      │  Đang dạy: 26 • Tạm nghỉ: 2      │
      └────────────────────────────────────┘
    """

    clicked = Signal()

    def __init__(self, icon_name: str, value: str, label: str,
                 accent: str = "#0099FF", parent=None):
        super().__init__(parent)
        self._accent = accent
        self.setFixedHeight(130)
        self.setObjectName("statCard")
        _apply_soft_shadow(self)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(5)

        # Top row: icon bubble + accent bar
        top = QHBoxLayout()
        top.setSpacing(0)

        r = int(accent[1:3], 16)
        g = int(accent[3:5], 16)
        b = int(accent[5:7], 16)

        icon_bubble = QWidget()
        icon_bubble.setFixedSize(42, 42)
        icon_bubble.setStyleSheet(
            f"QWidget{{background:rgba({r},{g},{b},45);"
            f"border-radius:10px;}}"
        )
        bubble_h = QHBoxLayout(icon_bubble)
        bubble_h.setContentsMargins(0, 0, 0, 0)
        bubble_h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_lbl = QLabel()
        self._icon_lbl.setStyleSheet("background:transparent;")
        self._icon_lbl.setPixmap(IconManager.get(icon_name, accent, 22).pixmap(22, 22))
        bubble_h.addWidget(self._icon_lbl)

        top.addWidget(icon_bubble)
        top.addStretch()

        bar = QFrame()
        bar.setObjectName("accentBar")
        bar.setFixedSize(40, 4)
        bar.setStyleSheet(f"background:{accent}; border-radius:2px;")
        top.addWidget(bar, alignment=Qt.AlignmentFlag.AlignVCenter)
        root.addLayout(top)

        root.addSpacing(2)

        # Value
        self._value_lbl = QLabel(value)
        self._value_lbl.setStyleSheet(
            f"font-size:28px; font-weight:700; color:{accent}; background:transparent;"
        )
        root.addWidget(self._value_lbl)

        # Label
        self._label_lbl = CaptionLabel(label, self)
        self._label_lbl.setStyleSheet("color:#8B949E; background:transparent;")
        root.addWidget(self._label_lbl)

        self._meta_lbl = CaptionLabel("", self)
        self._meta_lbl.setStyleSheet("color:#6E7681; background:transparent; font-size:11px;")
        self._meta_lbl.setWordWrap(False)
        self._meta_lbl.hide()
        root.addWidget(self._meta_lbl)
        root.addStretch()

        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_value(self, value: str):
        self._value_lbl.setText(value)

    def set_meta_text(self, text: str, color: str = "#6E7681"):
        self._meta_lbl.setText(text)
        self._meta_lbl.setStyleSheet(f"color:{color}; background: transparent;")
        self._meta_lbl.setVisible(bool(text))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class SectionHeader(QWidget):
    """Page-level header with title + subtitle."""

    def __init__(self, title: str, subtitle: str = "", icon: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("pageHeader")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(4)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(8)

        if icon:
            icon_lbl = QLabel(self)
            icon_lbl.setPixmap(IconManager.get(icon, "#76baff", 18).pixmap(18, 18))
            title_row.addWidget(icon_lbl)

        title_lbl = QLabel(title, self)
        title_lbl.setObjectName("pageTitle")
        title_row.addWidget(title_lbl)
        title_row.addStretch()
        layout.addLayout(title_row)

        if subtitle:
            sub_lbl = CaptionLabel(subtitle, self)
            sub_lbl.setObjectName("pageSubtitle")
            layout.addWidget(sub_lbl)

backend-demo
# components/pagination.py - Fluent-style pagination bar

from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from qfluentwidgets import PushButton, CaptionLabel, FluentIcon as FIF

# components/pagination.py — Fluent-style pagination bar

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from qfluentwidgets import PushButton, TransparentPushButton, CaptionLabel, FluentIcon as FIF
main


class PaginationBar(QWidget):
    """
    Emits page_changed(page: int) when the user navigates.
    Call update(current, total, page_size, item_count) to refresh state.
    """

    page_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
backend-demo
        self._current = 1
        self._total = 1

        self._current  = 1
        self._total    = 1
main
        self._page_size = 20
        self._item_count = 0

        layout = QHBoxLayout(self)
backend-demo
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(10)

        self._info_lbl = CaptionLabel("", self)
        self._info_lbl.setStyleSheet(
            "color: rgba(139,148,158,0.90); background: transparent; font-size: 12px;"
        )

        self._prev_btn = PushButton(FIF.PAGE_LEFT, "", self)
        self._prev_btn.setFixedSize(34, 34)
        self._prev_btn.setStyleSheet(self._nav_btn_qss())

        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(6)

        self._info_lbl = CaptionLabel("", self)
        self._info_lbl.setStyleSheet("color:rgba(160,175,200,0.6); background:transparent;")

        self._prev_btn = PushButton(FIF.PAGE_LEFT, "", self)
        self._prev_btn.setFixedSize(32, 32)
main
        self._prev_btn.clicked.connect(self._go_prev)

        self._page_lbl = CaptionLabel("1 / 1", self)
        self._page_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
backend-demo
        self._page_lbl.setFixedWidth(72)
        self._page_lbl.setStyleSheet(
            """
            color: #E6EDF3;
            font-weight: 600;
            font-size: 12px;
            padding: 6px 12px;
            border-radius: 12px;
            border: 1px solid rgba(88,166,255,0.35);
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(22,27,34,0.98),
                stop:1 rgba(31,111,235,0.14)
            );
            """
        )

        self._next_btn = PushButton(FIF.PAGE_RIGHT, "", self)
        self._next_btn.setFixedSize(34, 34)
        self._next_btn.setStyleSheet(self._nav_btn_qss())

        self._page_lbl.setFixedWidth(60)
        self._page_lbl.setStyleSheet(
            "color:rgba(200,210,230,0.85); background:transparent; font-weight:600;"
        )

        self._next_btn = PushButton(FIF.PAGE_RIGHT, "", self)
        self._next_btn.setFixedSize(32, 32)
main
        self._next_btn.clicked.connect(self._go_next)

        layout.addWidget(self._info_lbl)
        layout.addStretch()
        layout.addWidget(self._prev_btn)
        layout.addWidget(self._page_lbl)
        layout.addWidget(self._next_btn)

    def update_state(self, current: int, total: int,
                     page_size: int = 20, item_count: int = 0):
backend-demo
        self._current = max(1, current)
        self._total = max(1, total)
        self._page_size = page_size

        self._current    = max(1, current)
        self._total      = max(1, total)
        self._page_size  = page_size
main
        self._item_count = item_count

        self._page_lbl.setText(f"{self._current} / {self._total}")
        self._prev_btn.setEnabled(self._current > 1)
        self._next_btn.setEnabled(self._current < self._total)

        start = (self._current - 1) * page_size + 1
backend-demo
        end = start + item_count - 1
        self._info_lbl.setText(
            f"Hiển thị {start}-{end}" if item_count else "Không có dữ liệu"
        )

    @staticmethod
    def _nav_btn_qss() -> str:
        return """
        PushButton{
            color:#E6EDF3;
            border:1px solid #30363D;
            border-radius:10px;
            background-color: rgba(22,27,34,0.92);
        }
        PushButton:hover{
            border-color: rgba(88,166,255,0.70);
            background-color: rgba(45,51,59,0.95);
        }
        PushButton:pressed{
            border-color: rgba(56,139,253,0.95);
            background-color: rgba(17,88,199,0.22);
        }
        PushButton:disabled{
            color: rgba(139,148,158,0.45);
            border-color: rgba(48,54,61,0.55);
            background-color: rgba(13,17,23,0.70);
        }
        """


        end   = start + item_count - 1
        self._info_lbl.setText(
            f"Hiển thị {start}–{end}"
            if item_count else "Không có dữ liệu"
        )
main
    def _go_prev(self):
        if self._current > 1:
            self.page_changed.emit(self._current - 1)

    def _go_next(self):
        if self._current < self._total:
            self.page_changed.emit(self._current + 1)

    @property
    def current_page(self) -> int:
        return self._current

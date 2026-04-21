# components/pagination.py - Fluent-style pagination bar

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QWidget
from qfluentwidgets import CaptionLabel, FluentIcon as FIF, PushButton


class PaginationBar(QWidget):
    """
    Emits page_changed(page: int) when the user navigates.
    Call update_state(current, total, page_size, item_count) to refresh state.
    """

    page_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current = 1
        self._total = 1
        self._page_size = 20
        self._item_count = 0

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(10)

        self._info_lbl = CaptionLabel("", self)
        self._info_lbl.setStyleSheet(
            "color: rgba(139,148,158,0.90); background: transparent; font-size: 12px;"
        )

        self._prev_btn = PushButton(FIF.PAGE_LEFT, "", self)
        self._prev_btn.setFixedSize(34, 34)
        self._prev_btn.setStyleSheet(self._nav_btn_qss())
        self._prev_btn.clicked.connect(self._go_prev)

        self._page_lbl = CaptionLabel("1 / 1", self)
        self._page_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        self._next_btn.clicked.connect(self._go_next)

        layout.addWidget(self._info_lbl)
        layout.addStretch()
        layout.addWidget(self._prev_btn)
        layout.addWidget(self._page_lbl)
        layout.addWidget(self._next_btn)

    def update_state(self, current: int, total: int,
                     page_size: int = 20, item_count: int = 0):
        self._current = max(1, current)
        self._total = max(1, total)
        self._page_size = page_size
        self._item_count = item_count

        self._page_lbl.setText(f"{self._current} / {self._total}")
        self._prev_btn.setEnabled(self._current > 1)
        self._next_btn.setEnabled(self._current < self._total)

        start = (self._current - 1) * page_size + 1
        end = start + item_count - 1
        self._info_lbl.setText(
            f"Hiển thị {start}–{end}" if item_count else "Không có dữ liệu"
        )

    def update(self, current: int, total: int,
               page_size: int = 20, item_count: int = 0):
        self.update_state(current, total, page_size, item_count)

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

    def _go_prev(self):
        if self._current > 1:
            self.page_changed.emit(self._current - 1)

    def _go_next(self):
        if self._current < self._total:
            self.page_changed.emit(self._current + 1)

    @property
    def current_page(self) -> int:
        return self._current

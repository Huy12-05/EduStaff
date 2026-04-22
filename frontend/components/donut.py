# components/donut.py — Lightweight donut chart via QPainter
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QBrush, QColor


class DonutChart(QWidget):
    """Paints a segmented donut chart. Hole is transparent (composited over parent)."""

    def __init__(self, size: int = 90, hole: float = 0.58, parent=None):
        super().__init__(parent)
        self._data: list = []   # [(label, value, "#rrggbb"), ...]
        self._hole = hole
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def set_data(self, data: list):
        """data: list of (label, value, color_hex) tuples, zero-value entries ignored."""
        self._data = [(lbl, val, col) for lbl, val, col in data if val > 0]
        self.update()

    def paintEvent(self, event):
        if not self._data:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        m = 4
        rect = QRectF(m, m, w - 2 * m, h - 2 * m)

        total = sum(v for _, v, _ in self._data) or 1
        angle = 90.0  # start at 12-o'clock

        for _, value, color in self._data:
            span = value / total * 360.0
            p.setBrush(QBrush(QColor(color)))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawPie(rect, int(angle * 16), int(-span * 16))
            angle -= span

        # Punch transparent hole to create donut effect
        hole_r = (w - 2 * m) * self._hole / 2
        cx, cy = w / 2.0, h / 2.0
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        p.setBrush(Qt.GlobalColor.transparent)
        p.drawEllipse(QRectF(cx - hole_r, cy - hole_r, hole_r * 2, hole_r * 2))
        p.end()

# components/loading.py — Compact inline loading overlay

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame
from PySide6.QtCore import Qt
from qfluentwidgets import IndeterminateProgressBar, CaptionLabel


class LoadingOverlay(QWidget):
    """
    Semi-transparent overlay with a small compact spinner card.
    Attaches to parent widget; resize() whenever parent resizes.
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background: rgba(13,17,23,0.60);")
        self.hide()

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Compact card — max 160×68 px
        card = QFrame(self)
        card.setObjectName("loadingCard")
        card.setFixedSize(158, 66)
        card.setStyleSheet(
            "QFrame#loadingCard{"
            "background:rgba(39,36,49,0.97);"
            "border-radius:12px;"
            "border:1px solid #394165;}"
        )
        card_h = QHBoxLayout(card)
        card_h.setContentsMargins(16, 14, 16, 14)
        card_h.setSpacing(12)

        # Narrow progress bar used as spinner indicator
        self._bar = IndeterminateProgressBar(card)
        self._bar.setFixedSize(24, 24)

        self._label = CaptionLabel("Đang tải...", card)
        self._label.setStyleSheet("color:#8B949E; background:transparent; font-size:12px;")
        self._label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        card_h.addWidget(self._bar)
        card_h.addWidget(self._label)

        outer.addWidget(card)

    def set_text(self, text: str):
        self._label.setText(text)

    def show(self):
        self.resize(self.parent().size())
        self.raise_()
        super().show()

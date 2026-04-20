# components/loading.py - Compact loading overlay with fade animation

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import CaptionLabel, IndeterminateProgressRing


class LoadingOverlay(QWidget):
    """
    Semi-transparent overlay with a circular spinner card and 0.2s fade transitions.
    Attaches to parent widget; call resize() whenever parent resizes.
    """

    _FADE_MS = 200

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background: rgba(13,17,23,0.55);")
        self.hide()

        self._effect = QGraphicsOpacityEffect(self)
        self._effect.setOpacity(0.0)
        self.setGraphicsEffect(self._effect)

        self._anim = QPropertyAnimation(self._effect, b"opacity", self)
        self._anim.setDuration(self._FADE_MS)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.finished.connect(self._on_anim_finished)
        self._hiding = False

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame(self)
        card.setObjectName("loadingCard")
        card.setFixedSize(162, 62)
        card.setStyleSheet(
            "QFrame#loadingCard{"
            "background:rgba(39,36,49,0.97);"
            "border-radius:12px;"
            "border:1px solid #394165;}"
        )
        card_h = QHBoxLayout(card)
        card_h.setContentsMargins(14, 12, 18, 12)
        card_h.setSpacing(12)

        self._ring = IndeterminateProgressRing(card)
        self._ring.setFixedSize(26, 26)
        self._ring.setStrokeWidth(3)

        self._label = CaptionLabel("Dang tai...", card)
        self._label.setStyleSheet(
            "color:#8B949E; background:transparent; font-size:12px;"
        )
        self._label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        card_h.addWidget(self._ring)
        card_h.addWidget(self._label)
        outer.addWidget(card)

    def set_text(self, text: str):
        self._label.setText(text)

    def show(self):
        self._hiding = False
        self.resize(self.parent().size())
        self.raise_()
        super().show()
        self._anim.stop()
        self._anim.setStartValue(self._effect.opacity())
        self._anim.setEndValue(1.0)
        self._anim.start()

    def hide(self):
        if not self.isVisible():
            return
        self._hiding = True
        self._anim.stop()
        self._anim.setStartValue(self._effect.opacity())
        self._anim.setEndValue(0.0)
        self._anim.start()

    def _on_anim_finished(self):
        if self._hiding:
            super().hide()
            self._hiding = False

backend-demo
# components/loading.py — Compact loading overlay with fade animation

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from qfluentwidgets import IndeterminateProgressRing, CaptionLabel

# components/loading.py — Semi-transparent loading overlay

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from qfluentwidgets import IndeterminateProgressBar, BodyLabel
main


class LoadingOverlay(QWidget):
    """
backend-demo
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

        self._label = CaptionLabel("Đang tải...", card)
        self._label.setStyleSheet(
            "color:#8B949E; background:transparent; font-size:12px;"
        )
        self._label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        card_h.addWidget(self._ring)
        card_h.addWidget(self._label)

        outer.addWidget(card)

    Full-size translucent overlay with a spinner.
    Attach to a parent widget, resize() whenever parent resizes.
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background: rgba(13,17,23,0.75);")
        self.hide()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(14)

        # Spinner card
        card = QFrame(self)
        card.setObjectName("loadingCard")
        card.setStyleSheet(
            "QFrame#loadingCard{"
            "background:rgba(22,27,34,0.96);"
            "border-radius:16px;"
            "border:1px solid #30363D;}"
        )
        card_v = QVBoxLayout(card)
        card_v.setContentsMargins(32, 24, 32, 24)
        card_v.setSpacing(12)

        self._bar = IndeterminateProgressBar(card)
        self._bar.setFixedWidth(180)

        self._label = BodyLabel("Đang tải...", card)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet("color:#8B949E; background:transparent;")

        card_v.addWidget(self._bar)
        card_v.addWidget(self._label)

        layout.addWidget(card)
main

    def set_text(self, text: str):
        self._label.setText(text)

    def show(self):
backend-demo
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

        self.resize(self.parent().size())
        self.raise_()
        super().show()
main

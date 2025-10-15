"""
TextDialog - Composant d'affichage de texte pour jeux à choix
"""

from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from ..gui import GUIComponent, GUI
from ...config import (
    FONT_FAMILY, FONT_SIZE_TEXT, FONT_SIZE_SPEAKER,
    FONT_WEIGHT_TEXT, FONT_WEIGHT_SPEAKER,
    TEXT_COLOR, SPEAKER_COLOR,
    TEXT_BOX_OPACITY, BOX_BACKGROUND_R, BOX_BACKGROUND_G, BOX_BACKGROUND_B,
    BORDER_OPACITY, BORDER_RADIUS, TEXT_BOX_MARGIN, TEXT_BOX_PADDING
)


class TextDialogWidget(QWidget):
    """Widget Qt pour afficher un dialogue de texte."""

    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface du dialogue."""
        # Pas de style pour le widget principal (transparent)
        self.setStyleSheet("background-color: transparent;")

        # Box avec effet glassmorphism (utilise config)
        self.content_box = QWidget(self)
        self.content_box.setStyleSheet(f"""
            QWidget {{
                background-color: rgba({BOX_BACKGROUND_R}, {BOX_BACKGROUND_G}, {BOX_BACKGROUND_B}, {TEXT_BOX_OPACITY});
                border: 1px solid rgba(255, 255, 255, {BORDER_OPACITY});
                border-radius: {BORDER_RADIUS}px;
            }}
        """)

        # Label pour le speaker (utilise config)
        self.speaker_label = QLabel(self.content_box)
        self.speaker_label.setStyleSheet(f"""
            QLabel {{
                color: {SPEAKER_COLOR};
                font-family: {FONT_FAMILY};
                font-size: {FONT_SIZE_SPEAKER}px;
                font-weight: {FONT_WEIGHT_SPEAKER};
                background-color: transparent;
                border: none;
            }}
        """)
        self.speaker_label.hide()

        # Label pour le texte (utilise config)
        self.text_label = QLabel(self.content_box)
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.text_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_COLOR};
                font-family: {FONT_FAMILY};
                font-size: {FONT_SIZE_TEXT}px;
                font-weight: {FONT_WEIGHT_TEXT};
                background-color: transparent;
                border: none;
            }}
        """)

        # Indicateur "continuer"
        self.continue_label = QLabel("▼", self.content_box)
        self.continue_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.continue_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 14px;
                background-color: transparent;
                border: none;
            }
        """)

        # Gérer les clics
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def resizeEvent(self, event):
        """Repositionne les éléments quand le widget est redimensionné."""
        super().resizeEvent(event)
        width = self.width()
        height = self.height()

        # Positionner la box (utilise config pour les marges)
        self.content_box.setGeometry(TEXT_BOX_MARGIN, TEXT_BOX_MARGIN,
                                      width - 2*TEXT_BOX_MARGIN, height - 2*TEXT_BOX_MARGIN)

        # Positionner les éléments à l'intérieur de la box (utilise config pour padding)
        box_width = self.content_box.width()
        box_height = self.content_box.height()

        y_offset = TEXT_BOX_PADDING

        # Positionner le speaker
        if not self.speaker_label.isHidden():
            self.speaker_label.setGeometry(TEXT_BOX_PADDING, y_offset, box_width - 2*TEXT_BOX_PADDING, 25)
            y_offset += 35

        # Positionner le texte (prend presque tout l'espace disponible)
        continue_height = 25
        text_height = box_height - y_offset - continue_height - TEXT_BOX_PADDING
        self.text_label.setGeometry(TEXT_BOX_PADDING, y_offset, box_width - 2*TEXT_BOX_PADDING, text_height)

        # Positionner l'indicateur "continuer" en bas, centré
        continue_y = box_height - continue_height - 5
        self.continue_label.setGeometry(0, continue_y, box_width, continue_height)

    def set_content(self, text: str, speaker: Optional[str] = None):
        """Définit le contenu du dialogue."""
        self.text_label.setText(text)

        if speaker:
            self.speaker_label.setText(speaker)
            self.speaker_label.show()
        else:
            self.speaker_label.hide()

        # Déclencher un resize pour repositionner
        self.resizeEvent(None)

    def mousePressEvent(self, event):
        """Détecte les clics."""
        self.clicked.emit()

    def keyPressEvent(self, event):
        """Détecte les touches (Espace ou Entrée)."""
        if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.clicked.emit()


class TextDialogComponent(GUIComponent):
    """
    Composant pour afficher du texte dans une boîte de dialogue style visual novel.

    Affiche le texte en bas de l'écran avec un nom de personnage optionnel.
    L'utilisateur clique ou appuie sur Espace pour continuer.
    """

    def __init__(self, gui: GUI):
        super().__init__(gui)
        self.text: str = ""
        self.speaker: Optional[str] = None
        self._waiting = False
        self._continue_clicked = False

    def create_widget(self) -> QWidget:
        """Crée le widget Qt pour ce composant."""
        widget = TextDialogWidget()
        widget.clicked.connect(self._on_continue)
        return widget

    def show(self, text: str, speaker: Optional[str] = None, **kwargs) -> None:
        """
        Affiche le texte.

        Args:
            text: Texte à afficher
            speaker: Nom du personnage qui parle (optionnel)
            **kwargs: Paramètres supplémentaires
        """
        self.text = text
        self.speaker = speaker
        self.visible = True

        # Créer ou récupérer le widget
        if self.widget is None:
            self.widget = self.create_widget()

        # Mettre à jour le contenu
        self.widget.set_content(text, speaker)

        # Ajouter à la fenêtre
        if self.gui.window:
            self.gui.window.add_component_widget('text_dialog', self.widget)

        # Attendre que l'utilisateur clique
        self._wait_for_continue()

    def hide(self) -> None:
        """Cache le composant."""
        if self.gui.window and self.widget:
            self.gui.window.remove_component_widget('text_dialog')

        self.visible = False
        self.widget = None
        self.text = ""
        self.speaker = None

    def update(self, text: Optional[str] = None, speaker: Optional[str] = None, **kwargs) -> None:
        """
        Met à jour le contenu du composant.

        Args:
            text: Nouveau texte (ou None pour garder l'actuel)
            speaker: Nouveau speaker (ou None pour garder l'actuel)
            **kwargs: Paramètres supplémentaires
        """
        if text is not None:
            self.text = text
        if speaker is not None:
            self.speaker = speaker

        if self.widget and self.visible:
            self.widget.set_content(self.text, self.speaker)

    def _on_continue(self):
        """Appelé quand l'utilisateur clique pour continuer."""
        self._continue_clicked = True

    def _wait_for_continue(self):
        """Attend que l'utilisateur clique pour continuer."""
        import time

        self._continue_clicked = False
        self._waiting = True

        # Boucle d'attente avec process events et petit délai
        while not self._continue_clicked and self.visible:
            # Vérifier si un retour en arrière est demandé
            if self.gui.engine and self.gui.engine._go_back_requested:
                self._waiting = False
                return

            self.gui.process_events()
            time.sleep(0.01)

        self._waiting = False

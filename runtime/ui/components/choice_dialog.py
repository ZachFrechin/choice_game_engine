"""
ChoiceDialog - Composant de choix pour jeux à choix
"""

from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from ..gui import GUIComponent, GUI
from ...config import (
    FONT_FAMILY, FONT_SIZE_CHOICE, FONT_WEIGHT_CHOICE,
    CHOICE_COLOR, CHOICE_BOX_OPACITY,
    BOX_BACKGROUND_R, BOX_BACKGROUND_G, BOX_BACKGROUND_B,
    BORDER_OPACITY, BORDER_RADIUS, CHOICE_BOX_PADDING
)


class ChoiceButton(QPushButton):
    """Bouton stylisé pour un choix - design minimaliste."""

    def __init__(self, text: str, index: int):
        super().__init__(text)
        self.choice_index = index
        self.setup_style()

    def setup_style(self):
        """Configure le style du bouton (utilise config)."""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {CHOICE_COLOR};
                font-family: {FONT_FAMILY};
                font-size: {FONT_SIZE_CHOICE}px;
                font-weight: {FONT_WEIGHT_CHOICE};
                border: none;
                border-bottom: 1px solid rgba(255, 255, 255, 0.3);
                padding: {CHOICE_BOX_PADDING}px 25px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.5);
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.7);
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class ChoiceDialogWidget(QWidget):
    """Widget Qt pour afficher un dialogue de choix."""

    choice_selected = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.buttons: List[ChoiceButton] = []
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface du dialogue de choix."""
        # Pas de layout, positionnement manuel
        self.setStyleSheet("background-color: transparent;")

        # Container pour les choix (utilise config)
        self.choice_container = QWidget(self)
        self.choice_container.setStyleSheet(f"""
            QWidget {{
                background-color: rgba({BOX_BACKGROUND_R}, {BOX_BACKGROUND_G}, {BOX_BACKGROUND_B}, {CHOICE_BOX_OPACITY});
                border: 1px solid rgba(255, 255, 255, {BORDER_OPACITY});
                border-radius: {BORDER_RADIUS}px;
            }}
        """)

        # Layout pour le contenu du container
        self.choice_layout = QVBoxLayout(self.choice_container)
        self.choice_layout.setContentsMargins(0, 0, 0, 0)
        self.choice_layout.setSpacing(0)

        # Label pour la question
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet("""
            QLabel {
                color: #1a1a1a;
                font-size: 18px;
                font-weight: bold;
                padding: 30px 30px 20px 30px;
                background-color: transparent;
                border: none;
            }
        """)
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.choice_layout.addWidget(self.question_label)

    def resizeEvent(self, event):
        """Repositionne le container au centre quand le widget est redimensionné."""
        super().resizeEvent(event)

        # Ajuster la taille du container en fonction du contenu
        self.choice_container.adjustSize()

        # Centrer le container, mais laisser de l'espace en bas pour le TextDialog
        container_width = min(700, self.width() - 100)
        container_height = self.choice_container.sizeHint().height()

        # Réserver de l'espace pour le TextDialog en bas (environ 400px)
        available_height = self.height() - 420  # Espace pour TextDialog + marge

        x = (self.width() - container_width) // 2
        y = max(50, (available_height - container_height) // 2)  # Centré dans l'espace disponible

        self.choice_container.setGeometry(x, y, container_width, container_height)

    def set_content(self, question: str, choices: List[Dict[str, Any]]):
        """Définit le contenu du dialogue de choix."""
        self.question_label.setText(question)

        # Supprimer les anciens boutons
        for button in self.buttons:
            self.choice_layout.removeWidget(button)
            button.deleteLater()
        self.buttons.clear()

        # Créer les nouveaux boutons
        for i, choice in enumerate(choices):
            choice_text = choice.get('text', f'Choix {i+1}')
            button = ChoiceButton(choice_text, i)
            button.clicked.connect(lambda checked, idx=i: self.choice_selected.emit(idx))
            self.choice_layout.addWidget(button)
            self.buttons.append(button)

        # Forcer la mise à jour de la taille
        self.choice_container.adjustSize()
        self.resizeEvent(None)

    def keyPressEvent(self, event):
        """Détecte les touches numériques pour sélectionner un choix."""
        key = event.key()
        # Touches 1-9
        if Qt.Key.Key_1 <= key <= Qt.Key.Key_9:
            choice_idx = key - Qt.Key.Key_1
            if choice_idx < len(self.buttons):
                self.choice_selected.emit(choice_idx)


class ChoiceDialogComponent(GUIComponent):
    """
    Composant pour afficher des choix interactifs style visual novel.

    Affiche une question et des boutons de choix au centre de l'écran.
    L'utilisateur clique sur un bouton ou utilise les touches numériques.
    """

    def __init__(self, gui: GUI):
        super().__init__(gui)
        self.question: str = ""
        self.choices: List[Dict[str, Any]] = []
        self._selected_choice: Optional[int] = None
        self._waiting = False

    def create_widget(self) -> QWidget:
        """Crée le widget Qt pour ce composant."""
        widget = ChoiceDialogWidget()
        widget.choice_selected.connect(self._on_choice_selected)
        return widget

    def show(self, question: str, choices: List[Dict[str, Any]], **kwargs) -> int:
        """
        Affiche les choix et attend la sélection de l'utilisateur.

        Args:
            question: Question à afficher
            choices: Liste des choix (dicts avec 'text')
            **kwargs: Paramètres supplémentaires

        Returns:
            Index du choix sélectionné
        """
        self.question = question
        self.choices = choices
        self.visible = True

        # Créer ou récupérer le widget
        if self.widget is None:
            self.widget = self.create_widget()

        # Mettre à jour le contenu
        self.widget.set_content(question, choices)

        # Ajouter à la fenêtre
        if self.gui.window:
            self.gui.window.add_component_widget('choice_dialog', self.widget)

        # Donner le focus au widget pour les touches clavier
        self.widget.setFocus()

        # Attendre la sélection
        return self._wait_for_choice()

    def hide(self) -> None:
        """Cache le composant."""
        if self.gui.window and self.widget:
            self.gui.window.remove_component_widget('choice_dialog')

        self.visible = False
        self.widget = None
        self.question = ""
        self.choices = []
        self._selected_choice = None

    def update(self, question: Optional[str] = None, choices: Optional[List[Dict[str, Any]]] = None, **kwargs) -> None:
        """
        Met à jour le contenu du composant.

        Args:
            question: Nouvelle question (ou None pour garder l'actuelle)
            choices: Nouveaux choix (ou None pour garder les actuels)
            **kwargs: Paramètres supplémentaires
        """
        if question is not None:
            self.question = question
        if choices is not None:
            self.choices = choices

        if self.widget and self.visible:
            self.widget.set_content(self.question, self.choices)

    def _on_choice_selected(self, choice_idx: int):
        """Appelé quand l'utilisateur sélectionne un choix."""
        self._selected_choice = choice_idx

    def _wait_for_choice(self) -> int:
        """Attend que l'utilisateur sélectionne un choix."""
        import time

        self._selected_choice = None
        self._waiting = True

        # Boucle d'attente avec process events et petit délai
        while self._selected_choice is None and self.visible:
            # Vérifier si un retour en arrière est demandé
            if self.gui.engine and self.gui.engine._go_back_requested:
                self._waiting = False
                self.hide()
                return 0

            self.gui.process_events()
            time.sleep(0.01)

        self._waiting = False
        result = self._selected_choice if self._selected_choice is not None else 0

        # Cacher le composant après le choix
        self.hide()

        return result

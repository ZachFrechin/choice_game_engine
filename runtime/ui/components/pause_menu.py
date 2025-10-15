"""
PauseMenu - Menu de pause (Continuer/Sauvegarder/Charger/Quitter)
"""

from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from ..gui import GUIComponent, GUI
from ...config import (
    FONT_FAMILY, FONT_SIZE_MENU, FONT_WEIGHT_MENU,
    TEXT_COLOR, MENU_BOX_OPACITY,
    BOX_BACKGROUND_R, BOX_BACKGROUND_G, BOX_BACKGROUND_B
)


class PauseButton(QPushButton):
    """Bouton de menu pause stylisé."""

    def __init__(self, text: str):
        super().__init__(text)
        self.setup_style()

    def setup_style(self):
        """Configure le style du bouton."""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba({BOX_BACKGROUND_R}, {BOX_BACKGROUND_G}, {BOX_BACKGROUND_B}, {MENU_BOX_OPACITY});
                color: {TEXT_COLOR};
                font-family: {FONT_FAMILY};
                font-size: {FONT_SIZE_MENU}px;
                font-weight: {FONT_WEIGHT_MENU};
                border: none;
                padding: 15px 35px;
                margin: 6px 0px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 255);
            }}
            QPushButton:pressed {{
                background-color: rgba(220, 220, 225, 255);
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class PauseMenuWidget(QWidget):
    """Widget Qt pour le menu de pause."""

    action_selected = pyqtSignal(str)  # 'continue', 'save', 'load', 'quit'

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface du menu de pause."""
        self.setStyleSheet("background-color: rgba(0, 0, 0, 100);")  # Overlay semi-transparent

        # Container centré
        self.menu_container = QWidget(self)
        self.menu_container.setStyleSheet("""
            QWidget {
                background-color: rgba(200, 200, 205, 255);
                border: none;
            }
        """)

        layout = QVBoxLayout(self.menu_container)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(12)

        # Titre
        title_label = QLabel("PAUSE")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_COLOR};
                font-family: {FONT_FAMILY};
                font-size: 28px;
                font-weight: bold;
                padding-bottom: 25px;
                background-color: transparent;
            }}
        """)
        layout.addWidget(title_label)

        # Boutons
        continue_button = PauseButton("Continuer")
        continue_button.clicked.connect(lambda: self.action_selected.emit('continue'))
        layout.addWidget(continue_button)

        save_button = PauseButton("Sauvegarder")
        save_button.clicked.connect(lambda: self.action_selected.emit('save'))
        layout.addWidget(save_button)

        load_button = PauseButton("Charger")
        load_button.clicked.connect(lambda: self.action_selected.emit('load'))
        layout.addWidget(load_button)

        quit_button = PauseButton("Quitter")
        quit_button.clicked.connect(lambda: self.action_selected.emit('quit'))
        layout.addWidget(quit_button)

    def resizeEvent(self, event):
        """Repositionne le container au centre."""
        super().resizeEvent(event)

        container_width = 500
        container_height = 500

        x = (self.width() - container_width) // 2
        y = (self.height() - container_height) // 2

        self.menu_container.setGeometry(x, y, container_width, container_height)

    def keyPressEvent(self, event):
        """Détecte ESC pour continuer."""
        if event.key() == Qt.Key.Key_Escape:
            self.action_selected.emit('continue')


class PauseMenuComponent(GUIComponent):
    """
    Composant pour le menu de pause.

    Affiche les options: Continuer, Sauvegarder, Charger, Quitter.
    """

    def __init__(self, gui: GUI):
        super().__init__(gui)
        self._selected_action: Optional[str] = None
        self._waiting = False

    def create_widget(self) -> QWidget:
        """Crée le widget Qt pour ce composant."""
        widget = PauseMenuWidget()
        widget.action_selected.connect(self._on_action_selected)
        return widget

    def show(self, **kwargs) -> str:
        """
        Affiche le menu de pause et attend une action.

        Returns:
            Action sélectionnée ('continue', 'save', 'load', 'quit')
        """
        self.visible = True

        # Créer ou récupérer le widget
        if self.widget is None:
            self.widget = self.create_widget()

        # Ajouter à la fenêtre
        if self.gui.window:
            self.gui.window.add_component_widget('pause_menu', self.widget)

        # Donner le focus pour détecter ESC
        self.widget.setFocus()

        # Attendre la sélection
        return self._wait_for_action()

    def hide(self) -> None:
        """Cache le composant."""
        if self.gui.window and self.widget:
            self.gui.window.remove_component_widget('pause_menu')

        self.visible = False
        self.widget = None
        self._selected_action = None

    def update(self, **kwargs) -> None:
        """Met à jour le composant."""
        pass

    def _on_action_selected(self, action: str):
        """Appelé quand l'utilisateur sélectionne une action."""
        self._selected_action = action

    def _wait_for_action(self) -> str:
        """Attend que l'utilisateur sélectionne une action."""
        import time

        self._selected_action = None
        self._waiting = True

        while self._selected_action is None and self.visible:
            self.gui.process_events()
            time.sleep(0.01)

        self._waiting = False
        result = self._selected_action or 'continue'

        # Cacher le menu après la sélection
        self.hide()

        return result

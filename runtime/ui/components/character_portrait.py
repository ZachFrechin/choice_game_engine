"""
CharacterPortrait - Composant pour afficher l'image d'un personnage dans les dialogues
"""

from typing import Optional
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from ..gui import GUIComponent, GUI


class CharacterPortraitWidget(QWidget):
    """Widget Qt pour afficher le portrait d'un personnage."""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface du portrait."""
        # Label pour afficher l'image
        self.image_label = QLabel(self)
        self.image_label.setScaledContents(False)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Style par défaut (transparent)
        self.image_label.setStyleSheet("background-color: transparent;")

    def set_image(self, image_path: str):
        """
        Définit l'image du personnage.

        Args:
            image_path: Chemin vers l'image
        """
        if not Path(image_path).exists():
            print(f"⚠️  Image de personnage introuvable: {image_path}")
            self.clear_image()
            return

        # Charger l'image
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"⚠️  Impossible de charger l'image: {image_path}")
            self.clear_image()
            return

        # Adapter l'image à une taille fixe tout en gardant les proportions
        self.original_pixmap = pixmap
        self.update_pixmap()

    def update_pixmap(self):
        """Met à jour l'affichage de l'image en respectant les proportions."""
        if hasattr(self, 'original_pixmap'):
            # Redimensionner à une hauteur fixe (réduit à 300px)
            max_height = 300
            scaled_pixmap = self.original_pixmap.scaledToHeight(
                max_height,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.adjustSize()
            self.adjustSize()

    def clear_image(self):
        """Efface l'image du personnage."""
        self.image_label.clear()
        self.image_label.setPixmap(QPixmap())

    def resizeEvent(self, event):
        """Redimensionne l'image quand le widget change de taille."""
        super().resizeEvent(event)
        self.image_label.setGeometry(self.rect())


class CharacterPortraitComponent(GUIComponent):
    """
    Composant pour afficher le portrait d'un personnage.

    Utilisé conjointement avec TextDialogComponent pour créer
    une présentation visuelle du personnage qui parle.
    """

    def __init__(self, gui: GUI):
        super().__init__(gui)
        self.image_path: Optional[str] = None

    def create_widget(self) -> QWidget:
        """Crée le widget Qt pour ce composant."""
        return CharacterPortraitWidget()

    def show(self, image_path: str, **kwargs) -> None:
        """
        Affiche le portrait du personnage.

        Args:
            image_path: Chemin vers l'image du personnage
            **kwargs: Paramètres supplémentaires
        """
        # Ne rien afficher si le chemin est vide
        if not image_path or not image_path.strip():
            self.hide()
            return

        self.image_path = image_path
        self.visible = True

        # Créer ou récupérer le widget
        if self.widget is None:
            self.widget = self.create_widget()

        # Mettre à jour l'image
        self.widget.set_image(image_path)

        # Ajouter à la fenêtre
        if self.gui.window:
            self.gui.window.add_component_widget('character_portrait', self.widget)

    def hide(self) -> None:
        """Cache le composant."""
        if self.gui.window and self.widget:
            self.gui.window.remove_component_widget('character_portrait')

        self.visible = False
        if self.widget:
            self.widget.clear_image()
        self.widget = None
        self.image_path = None

    def update(self, image_path: Optional[str] = None, **kwargs) -> None:
        """
        Met à jour l'image du personnage.

        Args:
            image_path: Nouveau chemin d'image (ou None pour garder l'actuel)
            **kwargs: Paramètres supplémentaires
        """
        if image_path is not None:
            if not image_path or not image_path.strip():
                self.hide()
            else:
                self.show(image_path)

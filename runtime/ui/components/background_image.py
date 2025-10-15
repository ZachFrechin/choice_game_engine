"""
BackgroundImage - Composant d'image d'arrière-plan pour jeux à choix
"""

from typing import Optional
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from ..gui import GUIComponent, GUI


class BackgroundImageWidget(QWidget):
    """Widget Qt pour afficher une image d'arrière-plan."""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface de l'image d'arrière-plan."""
        # Label pour l'image en plein écran
        self.image_label = QLabel(self)
        self.image_label.setScaledContents(False)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: black;")

    def set_image(self, image_path: str):
        """
        Définit l'image d'arrière-plan.

        Args:
            image_path: Chemin vers l'image
        """
        if not Path(image_path).exists():
            print(f"⚠️  Image introuvable: {image_path}")
            self.image_label.setText("Image introuvable")
            self.image_label.setStyleSheet("""
                QLabel {
                    background-color: #1a1a2e;
                    color: #666;
                    font-size: 16px;
                }
            """)
            return

        # Charger l'image
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"⚠️  Impossible de charger l'image: {image_path}")
            self.image_label.setText("Erreur de chargement")
            return

        # Adapter l'image à la taille du widget
        self.original_pixmap = pixmap
        self.update_pixmap()

    def update_pixmap(self):
        """Met à jour l'affichage de l'image en respectant les proportions."""
        if hasattr(self, 'original_pixmap'):
            scaled_pixmap = self.original_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

    def clear_image(self):
        """Efface l'image d'arrière-plan."""
        self.image_label.clear()
        self.image_label.setStyleSheet("background-color: black;")

    def resizeEvent(self, event):
        """Redimensionne l'image quand le widget change de taille."""
        super().resizeEvent(event)
        self.image_label.setGeometry(self.rect())
        self.update_pixmap()


class BackgroundImageComponent(GUIComponent):
    """
    Composant pour afficher une image d'arrière-plan en plein écran.

    L'image est affichée derrière tous les autres composants et s'adapte
    automatiquement à la taille de la fenêtre.
    """

    def __init__(self, gui: GUI):
        super().__init__(gui)
        self.image_path: Optional[str] = None

    def create_widget(self) -> QWidget:
        """Crée le widget Qt pour ce composant."""
        return BackgroundImageWidget()

    def show(self, image_path: str, **kwargs) -> None:
        """
        Affiche l'image d'arrière-plan.

        Args:
            image_path: Chemin vers l'image à afficher
            **kwargs: Paramètres supplémentaires
        """
        self.image_path = image_path
        self.visible = True

        # Créer ou récupérer le widget
        if self.widget is None:
            self.widget = self.create_widget()

        # Mettre à jour l'image
        self.widget.set_image(image_path)

        # Ajouter à la fenêtre via add_component_widget
        if self.gui.window:
            self.gui.window.add_component_widget('background_image', self.widget)

    def hide(self) -> None:
        """Cache le composant."""
        if self.gui.window and self.widget:
            self.gui.window.remove_component_widget('background_image')

        self.visible = False
        self.widget = None
        self.image_path = None

    def update(self, image_path: Optional[str] = None, **kwargs) -> None:
        """
        Met à jour l'image d'arrière-plan.

        Args:
            image_path: Nouveau chemin d'image (ou None pour garder l'actuel)
            **kwargs: Paramètres supplémentaires
        """
        if image_path is not None:
            self.image_path = image_path

            if self.widget and self.visible:
                self.widget.set_image(self.image_path)

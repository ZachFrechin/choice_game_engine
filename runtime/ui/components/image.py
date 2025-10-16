"""
Image - Composant d'image avec système de layers pour jeux à choix
"""

from typing import Optional, Dict
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from ..gui import GUIComponent, GUI


class ImageWidget(QWidget):
    """Widget Qt pour afficher une image."""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface de l'image."""
        # Label pour l'image en plein écran
        self.image_label = QLabel(self)
        self.image_label.setScaledContents(False)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: transparent;")

    def set_image(self, image_path: str):
        """
        Définit l'image.

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
        """Efface l'image."""
        self.image_label.clear()
        self.image_label.setStyleSheet("background-color: transparent;")

    def resizeEvent(self, event):
        """Redimensionne l'image quand le widget change de taille."""
        super().resizeEvent(event)
        self.image_label.setGeometry(self.rect())
        self.update_pixmap()


class ImageComponent(GUIComponent):
    """
    Composant pour afficher des images en plein écran avec système de layers.

    Permet d'afficher plusieurs images superposées avec un z-order (layer).
    Layer 0 = arrière-plan, plus le nombre est élevé, plus l'image est au premier plan.
    """

    def __init__(self, gui: GUI):
        super().__init__(gui)
        # Dictionnaire des layers : {layer_id: {'widget': widget, 'image_path': path, 'layer': z_order}}
        self.layers: Dict[int, Dict] = {}

    def create_widget(self) -> QWidget:
        """Crée le widget Qt pour ce composant."""
        return ImageWidget()

    def show(self, image_path: str, layer: int = 0, **kwargs) -> None:
        """
        Affiche une image sur un layer spécifique.

        Args:
            image_path: Chemin vers l'image à afficher
            layer: Layer (z-order) pour cette image (0 = arrière-plan)
            **kwargs: Paramètres supplémentaires
        """
        # Si le layer existe déjà avec la même image, ne rien faire
        if layer in self.layers and self.layers[layer]['image_path'] == image_path:
            return

        # Créer ou mettre à jour le layer
        if layer not in self.layers:
            widget = self.create_widget()
            self.layers[layer] = {
                'widget': widget,
                'image_path': image_path,
                'layer': layer
            }
        else:
            # Réutiliser le widget existant
            widget = self.layers[layer]['widget']
            self.layers[layer]['image_path'] = image_path

        # Mettre à jour l'image
        widget.set_image(image_path)

        # Ajouter à la fenêtre avec le bon z-order
        if self.gui.window:
            # Nom unique pour chaque layer
            component_name = f'image_layer_{layer}'
            self.gui.window.add_component_widget(component_name, widget, z_order=layer)

        self.visible = True

    def hide(self, layer: Optional[int] = None) -> None:
        """
        Cache le composant.

        Args:
            layer: Layer spécifique à cacher, ou None pour tout cacher
        """
        if layer is not None:
            # Cacher un layer spécifique
            if layer in self.layers:
                if self.gui.window:
                    component_name = f'image_layer_{layer}'
                    self.gui.window.remove_component_widget(component_name)
                del self.layers[layer]
        else:
            # Cacher tous les layers
            if self.gui.window:
                for layer_id in list(self.layers.keys()):
                    component_name = f'image_layer_{layer_id}'
                    self.gui.window.remove_component_widget(component_name)
            self.layers.clear()

        # Marquer comme invisible si plus aucun layer
        if not self.layers:
            self.visible = False

    def update(self, image_path: Optional[str] = None, layer: int = 0, **kwargs) -> None:
        """
        Met à jour une image sur un layer.

        Args:
            image_path: Nouveau chemin d'image (ou None pour garder l'actuel)
            layer: Layer à mettre à jour
            **kwargs: Paramètres supplémentaires
        """
        if image_path is not None:
            self.show(image_path, layer)

    def get_layers(self) -> Dict[int, str]:
        """
        Retourne un dictionnaire des layers actifs.

        Returns:
            Dict[layer_id, image_path]
        """
        return {layer_id: data['image_path'] for layer_id, data in self.layers.items()}

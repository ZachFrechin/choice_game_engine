"""
Base widget pour les nodes Qt.
Version Qt du BaseNodeWidget compatible avec QGraphicsView.
"""

import copy
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class INodeWidget(ABC):
    """Interface pour les widgets de nodes Qt"""

    @abstractmethod
    def get_display_text(self) -> str:
        pass

    @abstractmethod
    def get_reduced_text(self) -> str:
        pass

    @abstractmethod
    def get_node_color(self) -> str:
        pass

    @abstractmethod
    def get_node_border_color(self) -> str:
        pass


class BaseNodeWidget(INodeWidget):
    """
    Classe de base pour les widgets de nodes.
    Simplifie la création de nouveaux types de nodes.
    """

    def __init__(self, canvas, node_id: str, node_type: str, data: Dict[str, Any]):
        self.canvas = canvas
        self.node_id = node_id
        self.node_type = node_type
        self.data = copy.deepcopy(data)
        self.width = 200
        self.height = 100

        # Récupérer l'item graphique du canvas
        self.item = canvas.node_items.get(node_id)
        print(f"[BaseNodeWidget] node_id={node_id}, item={self.item}, type={node_type}")
        if self.item:
            # Lier le widget à l'item pour que l'item puisse demander les ports dynamiquement
            self.item.node_widget = self

            # Appliquer les couleurs et le texte
            color = self.get_node_color()
            border = self.get_node_border_color()
            text = self.get_display_text()
            print(f"[BaseNodeWidget] Applying: color={color}, text={text[:30]}")
            self.item.set_colors(color, border)

            # Appliquer les ports (fallback initial)
            input_ports = self.get_input_ports()
            output_ports = self.get_output_ports()
            self.item.set_ports(input_ports, output_ports)

            self.refresh_display()
        else:
            print(f"[BaseNodeWidget] ERROR: No item found for node_id={node_id}")

    def get_node_color(self) -> str:
        """Couleur de fond du node. Override pour personnaliser."""
        return '#4a6fa5'

    def get_node_border_color(self) -> str:
        """Couleur de la bordure du node. Override pour personnaliser."""
        return '#6a8fc5'

    def get_node_shape(self) -> str:
        """Forme du node ('rect' ou 'diamond'). Override pour personnaliser."""
        return 'rect'

    def get_display_text(self) -> str:
        """Texte complet affiché dans le node. Override obligatoire."""
        return "Base Node"

    def get_reduced_text(self) -> str:
        """Texte réduit pour mode dezoomé. Override pour personnaliser."""
        full_text = self.get_display_text()
        first_line = full_text.split('\n')[0] if full_text else "Node"
        return first_line

    def get_input_ports(self) -> List[Dict[str, Any]]:
        """Ports d'entrée du node. Override pour personnaliser."""
        return [{'id': 'input', 'name': 'Entrée'}]

    def get_output_ports(self) -> List[Dict[str, Any]]:
        """Ports de sortie du node. Override pour personnaliser."""
        return [{'id': 'output', 'name': 'Sortie'}]

    def get_default_data(self) -> Dict[str, Any]:
        """Données par défaut du node. Override pour personnaliser."""
        return {}

    def refresh_display(self, reduced_mode: bool = False):
        """
        Rafraîchit l'affichage du node.
        Ne pas override (override get_display_text à la place).
        """
        if not self.item:
            return

        # Choisir le texte selon le mode
        if reduced_mode:
            display_text = self.get_reduced_text()
        else:
            display_text = self.get_display_text()

        self.item.set_display_text(display_text)

    def update_data(self, data: Dict[str, Any]):
        """Met à jour les données du node et rafraîchit l'affichage"""
        print(f"[BaseNodeWidget] update_data for {self.node_id}: old_data={self.data}, new_data={data}")
        self.data = copy.deepcopy(data)
        self.refresh_display()

        # Forcer le redessin pour mettre à jour les ports dynamiquement
        # L'item demandera get_input_ports() et get_output_ports() lors du paint()
        if self.item:
            print(f"[BaseNodeWidget] Forcing item.update() to redraw ports")
            # Notifier que la géométrie a changé (pour recalculer boundingRect)
            self.item.prepareGeometryChange()
            self.item.update()

    def create_on_change_callback(self, key: str, transform=None):
        """
        Crée un callback pour mettre à jour une clé spécifique dans self.data.
        Utile pour les éditeurs de propriétés.

        Args:
            key: Clé dans self.data à mettre à jour
            transform: Fonction optionnelle pour transformer la valeur avant sauvegarde

        Returns:
            Fonction callback prenant une valeur en paramètre
        """
        def callback(value):
            new_data = copy.deepcopy(self.data)
            if transform:
                value = transform(value)
            new_data[key] = value
            self.canvas.update_node_data(self.node_id, new_data)
            self.update_data(new_data)
        return callback

    def create_nested_on_change_callback(self, *keys, transform=None):
        """
        Crée un callback pour mettre à jour une clé imbriquée dans self.data.

        Args:
            *keys: Chemin de clés pour accéder à la valeur
            transform: Fonction optionnelle pour transformer la valeur

        Returns:
            Fonction callback
        """
        def callback(value):
            new_data = copy.deepcopy(self.data)
            if transform:
                value = transform(value)

            # Naviguer jusqu'à la clé parent
            current = new_data
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]

            # Mettre à jour la clé finale
            current[keys[-1]] = value
            self.canvas.update_node_data(self.node_id, new_data)
            self.update_data(new_data)
        return callback

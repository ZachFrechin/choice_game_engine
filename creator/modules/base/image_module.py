"""
Module Image - Nœud pour afficher une image avec système de layers

Nœud ovale violet qui prend un path d'image, un layer (z-order) et affiche une preview.
"""

from typing import Dict, List, Any
from ...core.interfaces.module_interface import IModule, NodeType
from ...ui.widgets.base_node_widget import BaseNodeWidget


class ImageNodeWidget(BaseNodeWidget):
    """
    Widget pour un noeud d'image.

    Affiche une preview de l'image sélectionnée avec son layer.
    """

    def get_node_shape(self) -> str:
        """Forme ovale pour le node image"""
        return 'ellipse'

    def get_node_color(self) -> str:
        """Couleur violette pour les nodes d'image"""
        return '#7a4f9a'

    def get_node_border_color(self) -> str:
        return '#9a6fba'

    def get_display_text(self) -> str:
        """Affiche une preview de l'image si disponible avec le layer"""
        image_path = self.data.get('image_path', '')
        layer = self.data.get('layer', 0)

        if not image_path:
            return f"🖼️ Image\nLayer {layer}\n\nAucune image"

        # Afficher juste le nom du fichier
        import os
        filename = os.path.basename(image_path)
        return f"🖼️ Image\nLayer {layer}\n\n{filename}"

    def get_default_data(self) -> Dict[str, Any]:
        """Données par défaut"""
        return {'image_path': '', 'layer': 0}

    def get_input_ports(self) -> List[Dict[str, Any]]:
        """Un port d'entrée"""
        return [{'id': 'input', 'name': 'Entrée'}]

    def get_output_ports(self) -> List[Dict[str, Any]]:
        """Un port de sortie"""
        return [{'id': 'output', 'name': 'Sortie'}]


class ImageModule(IModule):
    """Module pour les nœuds d'image"""

    @property
    def id(self) -> str:
        return "image"

    @property
    def name(self) -> str:
        return "Module Image"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Nœud pour afficher une image avec système de layers"

    def get_node_types(self) -> List[NodeType]:
        return [
            NodeType(
                type_id="image",
                display_name="Image",
                category="Visuel",
                icon="🖼️",
                default_data={'image_path': '', 'layer': 0},
                properties_schema={
                    'image_path': {
                        'type': 'file',
                        'label': 'Chemin de l\'image',
                        'required': True
                    },
                    'layer': {
                        'type': 'number',
                        'label': 'Layer (z-order)',
                        'required': True,
                        'default': 0
                    }
                }
            )
        ]

    def initialize(self):
        """Initialisation du module"""
        pass

    def cleanup(self):
        """Nettoyage du module"""
        pass

    def create_node_widget(self, node_type: str, canvas, node_id: str, x: float, y: float):
        """Crée le widget du node"""
        simple_type = node_type.split('.')[-1] if '.' in node_type else node_type

        if simple_type == "image":
            node = canvas.nodes.get(node_id)
            if node:
                widget = ImageNodeWidget(canvas, node_id, node_type, node['data'])
                return widget
        return None

    def serialize_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sérialise les données du node"""
        return node_data

    def deserialize_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Désérialise les données du node"""
        return node_data

    def create_properties_editor(self, node_type: str, parent, node, on_change_callback=None):
        """Crée l'éditeur de propriétés avec le helper create_file_field"""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpinBox
        from ...ui.editors.field_editors import create_file_field

        simple_type = node_type.split('.')[-1] if '.' in node_type else node_type

        if simple_type == "image":
            widget = QWidget(parent)
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)

            # Champ de fichier avec preview
            file_widget, _ = create_file_field(
                parent,
                "Chemin de l'image:",
                initial_value=node.data.get('image_path', ''),
                file_filter="Images (*.png *.jpg *.jpeg *.bmp *.gif)",
                on_change=node.widget.create_on_change_callback('image_path'),
                show_preview=True
            )
            layout.addWidget(file_widget)

            # Champ pour le layer (z-order)
            layer_label = QLabel("Layer (z-order):")
            layout.addWidget(layer_label)

            layer_spinbox = QSpinBox()
            layer_spinbox.setMinimum(-100)
            layer_spinbox.setMaximum(100)
            layer_spinbox.setValue(node.data.get('layer', 0))
            layer_spinbox.setToolTip("Layer 0 = arrière-plan, plus le nombre est élevé, plus l'image est au premier plan")
            layer_spinbox.valueChanged.connect(node.widget.create_on_change_callback('layer'))
            layout.addWidget(layer_spinbox)

            layout.addStretch()

            return widget

        return None

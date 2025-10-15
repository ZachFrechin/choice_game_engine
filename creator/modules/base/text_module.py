"""
Module Text - Nœud de texte simple

Exemple de module simplifié utilisant BaseNodeWidget et les composants d'éditeur réutilisables.
"""

from typing import Dict, List, Any
from ...core.interfaces.module_interface import IModule, NodeType
from ...ui.widgets.base_node_widget import BaseNodeWidget
from ...ui.editors.field_editors import create_multiline_field


class TextNodeWidget(BaseNodeWidget):
    """
    Widget pour un noeud de texte.

    Utilise BaseNodeWidget pour réduire le code nécessaire.
    Override uniquement les méthodes spécifiques au node text.
    """

    def get_node_color(self) -> str:
        """Couleur bleue pour les nodes de texte"""
        return '#3a5f8a'

    def get_node_border_color(self) -> str:
        return '#5a8fc5'

    def get_display_text(self) -> str:
        """Affiche un aperçu du contenu"""
        content = self.data.get('content', 'Texte...')
        preview = content[:50]
        if len(content) > 50:
            preview += '...'
        return f"📝 Texte\n\n{preview}"

    def get_default_data(self) -> Dict[str, Any]:
        """Données par défaut"""
        return {'content': 'Entrez votre texte ici...'}

    def get_input_ports(self) -> List[Dict[str, Any]]:
        """Un port d'entrée"""
        return [{'id': 'input', 'name': 'Entrée'}]

    def get_output_ports(self) -> List[Dict[str, Any]]:
        """Un port de sortie"""
        return [{'id': 'output', 'name': 'Sortie'}]


class TextModule(IModule):
    """Module pour les nœuds de texte"""

    @property
    def id(self) -> str:
        return "text"

    @property
    def name(self) -> str:
        return "Module Texte"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Nœud de texte simple pour afficher du contenu narratif"

    def get_node_types(self) -> List[NodeType]:
        return [
            NodeType(
                type_id="text",
                display_name="Texte",
                category="Base",
                icon="📝",
                default_data={'content': 'Entrez votre texte ici...', 'speaker': '', 'character_image': ''},
                properties_schema={
                    'content': {
                        'type': 'text',
                        'label': 'Contenu',
                        'multiline': True
                    },
                    'speaker': {
                        'type': 'text',
                        'label': 'Personnage (optionnel)'
                    },
                    'character_image': {
                        'type': 'file',
                        'label': 'Image du personnage (optionnel)',
                        'required': False
                    }
                }
            )
        ]

    def create_node_widget(self, node_type: str, canvas, node_id: str, x: float, y: float):
        """Crée le widget - simple et direct"""
        # Extraire le type simple (après le point)
        simple_type = node_type.split('.')[-1] if '.' in node_type else node_type
        print(f"[TextModule] create_node_widget: node_type={node_type}, simple_type={simple_type}")

        if simple_type == "text":
            # Récupérer les données du node depuis le canvas
            node = canvas.nodes.get(node_id)
            print(f"[TextModule] Node data: {node}")
            if node:
                widget = TextNodeWidget(canvas, node_id, node_type, node['data'])
                print(f"[TextModule] Created widget: {widget}")
                return widget
            else:
                print(f"[TextModule] ERROR: No node found for node_id={node_id}")
        else:
            print(f"[TextModule] simple_type '{simple_type}' != 'text', returning None")
        return None

    def serialize_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        return node_data

    def deserialize_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        return node_data

    def create_properties_editor(self, node_type: str, parent, node, on_change_callback=None):
        """
        Crée l'éditeur de propriétés en utilisant les composants réutilisables.

        Beaucoup plus simple qu'avant grâce aux helpers !
        """
        from PyQt6.QtWidgets import QWidget, QVBoxLayout
        from ...ui.editors.field_editors import create_text_field, create_file_field

        # Extraire le type simple (après le point)
        simple_type = node_type.split('.')[-1] if '.' in node_type else node_type

        if simple_type == "text":
            container = QWidget(parent)
            layout = QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)

            # Champ texte du contenu
            content_frame, _ = create_multiline_field(
                container,
                label="Contenu:",
                initial_value=node.data.get('content', ''),
                height=8,
                on_change=node.widget.create_on_change_callback('content')
            )
            layout.addWidget(content_frame)

            # Champ speaker (optionnel)
            speaker_frame, _ = create_text_field(
                container,
                label="Personnage (optionnel):",
                initial_value=node.data.get('speaker', ''),
                on_change=node.widget.create_on_change_callback('speaker')
            )
            layout.addWidget(speaker_frame)

            # Champ image du personnage (optionnel)
            image_frame, _ = create_file_field(
                container,
                label="Image du personnage (optionnel):",
                initial_value=node.data.get('character_image', ''),
                file_filter="Images (*.png *.jpg *.jpeg *.bmp *.gif)",
                on_change=node.widget.create_on_change_callback('character_image'),
                show_preview=True
            )
            layout.addWidget(image_frame)

            layout.addStretch()

            return container
        return None

    def validate_node(self, node_data: Dict[str, Any]) -> List[str]:
        """Validation optionnelle"""
        errors = []
        data = node_data.get('data', {})
        content = data.get('content', '')
        if not content or not content.strip():
            errors.append("Le contenu du texte ne peut pas être vide")
        return errors

"""
Module Music - Nœud pour jouer de la musique avec système de pistes

Nœud ovale bleu qui prend un path vers un fichier audio, une piste et une option repeat.
"""

from typing import Dict, List, Any
from ...core.interfaces.module_interface import IModule, NodeType
from ...ui.widgets.base_node_widget import BaseNodeWidget


class MusicNodeWidget(BaseNodeWidget):
    """
    Widget pour un noeud de musique.

    Affiche le nom du fichier audio sélectionné avec sa piste et son mode repeat.
    """

    def get_node_shape(self) -> str:
        """Forme ovale pour le music node"""
        return 'ellipse'

    def get_node_color(self) -> str:
        """Couleur bleue pour les nodes de musique"""
        return '#4a7a9a'

    def get_node_border_color(self) -> str:
        return '#6a9aba'

    def get_display_text(self) -> str:
        """Affiche le nom du fichier audio avec la piste et le mode repeat"""
        music_path = self.data.get('music_path', '')
        track = self.data.get('track', 0)
        repeat = self.data.get('repeat', True)

        repeat_text = "🔁" if repeat else "▶️"

        if not music_path:
            return f"🎵 Music\nTrack {track} {repeat_text}\n\nAucune musique"

        # Afficher juste le nom du fichier
        import os
        filename = os.path.basename(music_path)
        return f"🎵 Music\nTrack {track} {repeat_text}\n\n{filename}"

    def get_default_data(self) -> Dict[str, Any]:
        """Données par défaut"""
        return {'music_path': '', 'track': 0, 'repeat': True}

    def get_input_ports(self) -> List[Dict[str, Any]]:
        """Un port d'entrée"""
        return [{'id': 'input', 'name': 'Entrée'}]

    def get_output_ports(self) -> List[Dict[str, Any]]:
        """Un port de sortie"""
        return [{'id': 'output', 'name': 'Sortie'}]


class MusicModule(IModule):
    """Module pour les nœuds de musique"""

    @property
    def id(self) -> str:
        return "music"

    @property
    def name(self) -> str:
        return "Module Music"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Nœud pour jouer de la musique avec système de pistes et option repeat"

    def get_node_types(self) -> List[NodeType]:
        return [
            NodeType(
                type_id="music",
                display_name="Music",
                category="Audio",
                icon="🎵",
                default_data={'music_path': '', 'track': 0, 'repeat': True},
                properties_schema={
                    'music_path': {
                        'type': 'file',
                        'label': 'Chemin du fichier audio',
                        'required': True
                    },
                    'track': {
                        'type': 'number',
                        'label': 'Piste audio',
                        'required': True,
                        'default': 0
                    },
                    'repeat': {
                        'type': 'boolean',
                        'label': 'Répéter en boucle',
                        'required': True,
                        'default': True
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

        if simple_type == "music":
            node = canvas.nodes.get(node_id)
            if node:
                widget = MusicNodeWidget(canvas, node_id, node_type, node['data'])
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
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSpinBox, QCheckBox
        from ...ui.editors.field_editors import create_file_field

        simple_type = node_type.split('.')[-1] if '.' in node_type else node_type

        if simple_type == "music":
            widget = QWidget(parent)
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)

            # Utiliser le composant réutilisable pour sélectionner un fichier audio
            file_widget, _ = create_file_field(
                parent,
                "Chemin du fichier audio:",
                initial_value=node.data.get('music_path', ''),
                file_filter="Audio (*.mp3 *.wav *.ogg *.flac *.m4a)",
                on_change=node.widget.create_on_change_callback('music_path'),
                show_preview=False
            )
            layout.addWidget(file_widget)

            # Champ pour la piste (track)
            track_label = QLabel("Piste audio:")
            layout.addWidget(track_label)

            track_spinbox = QSpinBox()
            track_spinbox.setMinimum(0)
            track_spinbox.setMaximum(10)
            track_spinbox.setValue(node.data.get('track', 0))
            track_spinbox.setToolTip("Piste 0 = musique de fond principale, autres pistes = effets sonores superposés")
            track_spinbox.valueChanged.connect(node.widget.create_on_change_callback('track'))
            layout.addWidget(track_spinbox)

            # Checkbox pour repeat
            repeat_checkbox = QCheckBox("Répéter en boucle")
            repeat_checkbox.setChecked(node.data.get('repeat', True))
            repeat_checkbox.setToolTip("Si coché, le son se répète en boucle. Sinon, il ne joue qu'une fois.")
            repeat_checkbox.toggled.connect(node.widget.create_on_change_callback('repeat'))
            layout.addWidget(repeat_checkbox)

            layout.addStretch()

            return widget

        return None

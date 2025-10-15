"""
Module Choice - Nœud de choix multiples avec ports dynamiques

Exemple de module avec ports dynamiques utilisant BaseNodeWidget et les composants d'éditeur.
"""

from typing import Dict, List, Any
from ...core.interfaces.module_interface import IModule, NodeType
from ...ui.widgets.base_node_widget import BaseNodeWidget
from ...ui.editors import create_multiline_field, create_dynamic_list_editor
from ...core.linting import LintIssue, LintSeverity


class ChoiceNodeWidget(BaseNodeWidget):
    """
    Widget pour un noeud de choix avec ports de sortie dynamiques.

    Les ports de sortie sont automatiquement créés en fonction du nombre de choix.
    """

    def get_node_color(self) -> str:
        """Couleur marron pour les nodes de choix"""
        return '#8a5f3a'

    def get_node_border_color(self) -> str:
        return '#c58f5a'

    def get_display_text(self) -> str:
        """Affiche la question et le nombre de choix"""
        question = self.data.get('question', 'Question?')
        preview = question[:40]
        if len(question) > 40:
            preview += '...'

        choice_count = len(self.data.get('choices', []))
        return f"❓ Choix\n\n{preview}\n\n{choice_count} choix disponibles"

    def get_default_data(self) -> Dict[str, Any]:
        """Données par défaut avec 2 choix"""
        return {
            'question': 'Que faites-vous?',
            'choices': [
                {'text': 'Choix 1'},
                {'text': 'Choix 2'}
            ]
        }

    def get_input_ports(self) -> List[Dict[str, Any]]:
        """Un port d'entrée"""
        return [{'id': 'input', 'name': 'Entrée'}]

    def get_output_ports(self) -> List[Dict[str, Any]]:
        """
        Ports dynamiques basés sur le nombre de choix.
        C'est ici que la magie opère !
        """
        choices = self.data.get('choices', [])
        ports = [
            {'id': f'output_{i}', 'name': choice.get('text', f'Choix {i+1}')}
            for i, choice in enumerate(choices)
        ]
        print(f"[ChoiceNodeWidget] get_output_ports() for {self.node_id}: {len(ports)} ports, choices={choices}")
        return ports


class ChoiceModule(IModule):
    """Module pour les nœuds de choix"""

    @property
    def id(self) -> str:
        return "choice"

    @property
    def name(self) -> str:
        return "Module Choix"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Nœud de choix multiples avec ports dynamiques"

    def get_node_types(self) -> List[NodeType]:
        return [
            NodeType(
                type_id="choice",
                display_name="Choix",
                category="Base",
                icon="❓",
                default_data={
                    'question': 'Que faites-vous?',
                    'choices': [
                        {'text': 'Choix 1'},
                        {'text': 'Choix 2'}
                    ]
                },
                properties_schema={
                    'question': {'type': 'text', 'label': 'Question', 'multiline': True},
                    'choices': {'type': 'list', 'label': 'Choix'}
                }
            )
        ]

    def create_node_widget(self, node_type: str, canvas, node_id: str, x: float, y: float):
        """Crée le widget"""
        # Extraire le type simple (après le point)
        simple_type = node_type.split('.')[-1] if '.' in node_type else node_type

        if simple_type == "choice":
            node = canvas.nodes.get(node_id)
            if node:
                return ChoiceNodeWidget(canvas, node_id, node_type, node['data'])
        return None

    def serialize_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        return node_data

    def deserialize_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        return node_data

    def create_properties_editor(self, node_type: str, parent, node, on_change_callback=None):
        """
        Éditeur simplifié grâce aux composants réutilisables !

        Comparer avec l'ancien code : de ~90 lignes à ~20 lignes !
        """
        # Extraire le type simple (après le point)
        simple_type = node_type.split('.')[-1] if '.' in node_type else node_type

        if simple_type != "choice":
            return None

        # Créer un conteneur pour tous les champs
        from PyQt6.QtWidgets import QWidget, QVBoxLayout
        container = QWidget(parent)
        layout = QVBoxLayout()
        container.setLayout(layout)

        # Question
        question_frame, _ = create_multiline_field(
            container,
            label="Question:",
            initial_value=node.data.get('question', ''),
            height=3,
            on_change=node.widget.create_on_change_callback('question')
        )
        layout.addWidget(question_frame)

        # Liste de choix dynamique
        def on_choices_change(choices):
            """Callback appelé quand la liste change"""
            print(f"[ChoiceModule] on_choices_change called with {len(choices)} choices: {choices}")
            new_data = {
                **node.data,
                'choices': choices
            }
            print(f"[ChoiceModule] Updating node data to: {new_data}")
            node.widget.canvas.update_node_data(node.widget.node_id, new_data)
            node.widget.update_data(new_data)

        list_frame = create_dynamic_list_editor(
            container,
            label="Choix:",
            items=node.data.get('choices', []),
            item_template={'text': 'Nouveau choix'},
            field_config=[{'key': 'text', 'label': 'Texte', 'width': 30}],
            on_change=on_choices_change,
            add_button_text="+ Ajouter un choix"
        )
        layout.addWidget(list_frame)

        return container

    def validate(self, node_data: Dict[str, Any], graph_context: Dict[str, Any]) -> List[LintIssue]:
        """
        Valide un nœud de choix.

        Vérifie:
        - Que la question n'est pas vide
        - Qu'il y a au moins 2 choix
        - Que tous les choix ont du texte
        """
        issues = []
        node_id = node_data.get('id', 'unknown')
        data = node_data.get('data', {})

        question = data.get('question', '').strip()
        choices = data.get('choices', [])

        # Vérifier que la question n'est pas vide
        if not question:
            issues.append(LintIssue(
                node_id=node_id,
                severity=LintSeverity.ERROR,
                message="Question is empty",
                details="A choice node must have a question to display to the player."
            ))

        # Vérifier qu'il y a au moins 2 choix
        if len(choices) < 2:
            issues.append(LintIssue(
                node_id=node_id,
                severity=LintSeverity.ERROR,
                message=f"Choice node has only {len(choices)} choice(s)",
                details="A choice node must have at least 2 choices. Add more choices or use a different node type."
            ))

        # Vérifier que tous les choix ont du texte
        for i, choice in enumerate(choices):
            if not choice.get('text', '').strip():
                issues.append(LintIssue(
                    node_id=node_id,
                    severity=LintSeverity.ERROR,
                    message=f"Choice #{i+1} is empty",
                    details=f"Choice #{i+1} has no text. Each choice must have descriptive text."
                ))

        return issues

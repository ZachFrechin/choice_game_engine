"""
Module MassInit - Permet d'initialiser plusieurs variables en une seule fois
"""

from typing import Dict, List, Any
from ...core.interfaces.module_interface import IModule, NodeType
from ...ui.widgets.base_node_widget import BaseNodeWidget
from ...ui.editors import create_dynamic_list_editor
from ...core.linting import LintIssue, LintSeverity


class MassInitNodeWidget(BaseNodeWidget):
    """Widget pour un nœud d'initialisation de masse"""

    def get_node_color(self) -> str:
        """Couleur violette pour les nodes de variables"""
        return '#6a4a8a'

    def get_node_border_color(self) -> str:
        return '#9a6aca'

    def get_display_text(self) -> str:
        """Affiche le nombre de variables initialisées"""
        variables = self.data.get('variables', [])
        var_count = len(variables)

        if var_count == 0:
            return "📦 Mass Init\n\nAucune variable"
        elif var_count == 1:
            var = variables[0]
            return f"📦 Mass Init\n\n{var.get('name', '?')} = {var.get('value', 0)}"
        else:
            preview = ", ".join([v.get('name', '?') for v in variables[:3]])
            if var_count > 3:
                preview += "..."
            return f"📦 Mass Init\n\n{var_count} variables\n{preview}"

    def get_default_data(self) -> Dict[str, Any]:
        return {
            'variables': [
                {'name': 'var1', 'value': 0},
                {'name': 'var2', 'value': 'hello'}
            ]
        }

    def get_input_ports(self) -> List[Dict[str, Any]]:
        return [{'id': 'input', 'name': 'Entrée'}]

    def get_output_ports(self) -> List[Dict[str, Any]]:
        return [{'id': 'output', 'name': 'Sortie'}]


class MassInitModule(IModule):
    """Module pour l'initialisation de masse de variables"""

    @property
    def id(self) -> str:
        return "massinit"

    @property
    def name(self) -> str:
        return "Module Mass Init"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Initialise plusieurs variables en une seule fois"

    def get_node_types(self) -> List[NodeType]:
        return [
            NodeType(
                type_id="massinit",
                display_name="Mass Init",
                category="Variables",
                icon="📦",
                default_data={
                    'variables': [
                        {'name': 'var1', 'value': 0},
                        {'name': 'var2', 'value': 'hello'}
                    ]
                },
                properties_schema={}
            )
        ]

    def create_node_widget(self, node_type: str, canvas, node_id: str, x: float, y: float):
        """Crée le widget"""
        simple_type = node_type.split('.')[-1] if '.' in node_type else node_type

        if simple_type == "massinit":
            node = canvas.nodes.get(node_id)
            if node:
                return MassInitNodeWidget(canvas, node_id, node_type, node['data'])
        return None

    def serialize_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        return node_data

    def deserialize_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        return node_data

    def create_properties_editor(self, node_type: str, parent, node, on_change_callback=None):
        """Éditeur pour le nœud MassInit"""
        simple_type = node_type.split('.')[-1] if '.' in node_type else node_type

        if simple_type != "massinit":
            return None

        # Créer un conteneur pour tous les champs
        from PyQt6.QtWidgets import QWidget, QVBoxLayout
        container = QWidget(parent)
        layout = QVBoxLayout()
        container.setLayout(layout)

        # Liste de variables dynamique
        def on_variables_change(variables):
            """Callback appelé quand la liste change"""
            # Convertir les valeurs numériques si possible
            processed_vars = []
            for var in variables:
                processed_var = var.copy()
                value = var.get('value', '0')
                # Essayer de convertir en nombre si possible
                try:
                    if '.' in str(value):
                        processed_var['value'] = float(value)
                    else:
                        processed_var['value'] = int(value)
                except (ValueError, TypeError):
                    # Garder comme string si ce n'est pas un nombre
                    processed_var['value'] = str(value)
                processed_vars.append(processed_var)

            print(f"[MassInitModule] Variables changed: {processed_vars}")
            new_data = {
                **node.data,
                'variables': processed_vars
            }
            node.widget.canvas.update_node_data(node.widget.node_id, new_data)
            node.widget.update_data(new_data)

        list_frame = create_dynamic_list_editor(
            container,
            label="Variables:",
            items=node.data.get('variables', []),
            item_template={'name': 'nouvelle_var', 'value': '0'},
            field_config=[
                {'key': 'name', 'label': 'Nom', 'width': 15},
                {'key': 'value', 'label': 'Valeur (text/nombre)', 'width': 20}
            ],
            on_change=on_variables_change,
            add_button_text="+ Ajouter une variable"
        )
        layout.addWidget(list_frame)

        return container

    def validate(self, node_data: Dict[str, Any], graph_context: Dict[str, Any]) -> List[LintIssue]:
        """
        Valide un nœud MassInit.

        Vérifie:
        - Qu'il y a au moins une variable
        - Que tous les noms de variables ne sont pas vides
        - Qu'il n'y a pas de doublons de noms
        """
        issues = []
        node_id = node_data.get('id', 'unknown')
        data = node_data.get('data', {})
        variables = data.get('variables', [])

        # Vérifier qu'il y a au moins une variable
        if len(variables) == 0:
            issues.append(LintIssue(
                node_id=node_id,
                severity=LintSeverity.WARNING,
                message="MassInit has no variables",
                details="Add at least one variable to initialize."
            ))
            return issues

        # Vérifier que tous les noms sont remplis
        seen_names = set()
        for i, var in enumerate(variables):
            name = var.get('name', '').strip()

            if not name:
                issues.append(LintIssue(
                    node_id=node_id,
                    severity=LintSeverity.ERROR,
                    message=f"Variable #{i+1} has no name",
                    details=f"Variable at position {i+1} needs a name."
                ))
            else:
                # Vérifier les doublons
                if name in seen_names:
                    issues.append(LintIssue(
                        node_id=node_id,
                        severity=LintSeverity.WARNING,
                        message=f"Duplicate variable name '{name}'",
                        details=f"The variable '{name}' appears multiple times in this MassInit node. The last value will be used."
                    ))
                seen_names.add(name)

        return issues

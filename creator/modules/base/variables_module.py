"""
Module Variables - Module de base pour variables et conditions

Exemple de module avec plusieurs types de nodes (variable et condition).
"""

from typing import Dict, List, Any
from ...core.interfaces.module_interface import IModule, NodeType
from ...ui.widgets.base_node_widget import BaseNodeWidget
from ...ui.editors import create_text_field, create_number_field, create_dropdown_field, create_radio_buttons
from ...core.linting import LintIssue, LintSeverity
from PyQt6.QtWidgets import QWidget, QVBoxLayout


class VariableNodeWidget(BaseNodeWidget):
    """Widget pour un noeud de variable"""

    def get_node_color(self) -> str:
        """Couleur violette pour les nodes de variable"""
        return '#5a3a8a'

    def get_node_border_color(self) -> str:
        return '#8a5ac5'

    def get_display_text(self) -> str:
        """Affiche l'opération sur la variable"""
        var_name = self.data.get('variable', 'var')
        operation = self.data.get('operation', 'set')
        value = self.data.get('value', 0)

        op_symbol = {
            'set': '=',
            'add': '+=',
            'subtract': '-=',
            'multiply': '*='
        }.get(operation, '=')

        return f"💾 Variable\n\n{var_name} {op_symbol} {value}"

    def get_default_data(self) -> Dict[str, Any]:
        return {'variable': 'score', 'operation': 'set', 'value': 0, 'value_type': 'number'}

    def get_input_ports(self) -> List[Dict[str, Any]]:
        return [{'id': 'input', 'name': 'Entrée'}]

    def get_output_ports(self) -> List[Dict[str, Any]]:
        return [{'id': 'output', 'name': 'Sortie'}]


class ConditionNodeWidget(BaseNodeWidget):
    """Widget pour un noeud de condition"""

    def get_node_color(self) -> str:
        """Couleur rouge pour les nodes de condition"""
        return '#8a3a3a'

    def get_node_border_color(self) -> str:
        return '#c55a5a'

    def get_node_shape(self) -> str:
        """Forme losange pour les conditions"""
        return 'diamond'

    def get_display_text(self) -> str:
        """Affiche la condition"""
        var_name = self.data.get('variable', 'var')
        operator = self.data.get('operator', '==')
        value = self.data.get('value', 0)

        return f"🔀 Condition\n\n{var_name} {operator} {value}"

    def get_default_data(self) -> Dict[str, Any]:
        return {'variable': 'score', 'operator': '==', 'value': 0}

    def get_input_ports(self) -> List[Dict[str, Any]]:
        return [{'id': 'input', 'name': 'Entrée'}]

    def get_output_ports(self) -> List[Dict[str, Any]]:
        """Deux sorties : vrai et faux"""
        return [
            {'id': 'output_true', 'name': 'Vrai'},
            {'id': 'output_false', 'name': 'Faux'}
        ]


class VariablesModule(IModule):
    """Module pour les variables et conditions"""

    @property
    def id(self) -> str:
        return "variables"

    @property
    def name(self) -> str:
        return "Module Variables"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Système de variables et conditions pour créer des jeux avec états"

    def get_node_types(self) -> List[NodeType]:
        return [
            NodeType(
                type_id="variable",
                display_name="Variable",
                category="Base",
                icon="💾",
                default_data={'variable': 'score', 'operation': 'set', 'value': 0},
                properties_schema={}
            ),
            NodeType(
                type_id="condition",
                display_name="Condition",
                category="Base",
                icon="🔀",
                default_data={'variable': 'score', 'operator': '==', 'value': 0},
                properties_schema={}
            )
        ]

    def create_node_widget(self, node_type: str, canvas, node_id: str, x: float, y: float):
        """Crée le widget selon le type"""
        node = canvas.nodes.get(node_id)
        if not node:
            return None

        # Extraire le type simple (après le point)
        simple_type = node_type.split('.')[-1] if '.' in node_type else node_type

        if simple_type == "variable":
            return VariableNodeWidget(canvas, node_id, node_type, node['data'])
        elif simple_type == "condition":
            return ConditionNodeWidget(canvas, node_id, node_type, node['data'])
        return None

    def serialize_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        return node_data

    def deserialize_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        return node_data

    def create_properties_editor(self, node_type: str, parent, node, on_change_callback=None):
        """
        Éditeur simplifié pour les deux types de nodes.
        """
        # Extraire le type simple (après le point)
        simple_type = node_type.split('.')[-1] if '.' in node_type else node_type

        if simple_type == "variable":
            return self._create_variable_editor(parent, node)
        elif simple_type == "condition":
            return self._create_condition_editor(parent, node)
        return None

    def _create_variable_editor(self, parent, node):
        """Éditeur pour un noeud variable"""
        container = QWidget(parent)
        layout = QVBoxLayout()
        container.setLayout(layout)

        # Nom de la variable
        var_frame, _ = create_text_field(
            container,
            label="Variable:",
            initial_value=node.data.get('variable', 'score'),
            on_change=node.widget.create_on_change_callback('variable')
        )
        layout.addWidget(var_frame)

        # Opération
        def on_operation_change(value):
            callback = node.widget.create_on_change_callback('operation')
            callback(value)

        op_frame, _ = create_radio_buttons(
            container,
            label="Opération:",
            options=[
                ('set', 'Définir (=)'),
                ('add', 'Ajouter (+=)'),
                ('subtract', 'Soustraire (-=)'),
                ('multiply', 'Multiplier (*=)')
            ],
            initial_value=node.data.get('operation', 'set'),
            on_change=on_operation_change
        )
        layout.addWidget(op_frame)

        # Type de valeur
        def on_type_change(value):
            callback = node.widget.create_on_change_callback('value_type')
            callback(value)
            # Recréer l'éditeur pour changer le champ
            # On émet un signal de sélection pour forcer le refresh
            node.widget.canvas.node_selected.emit(node.widget.node_id)

        type_frame, _ = create_radio_buttons(
            container,
            label="Type de valeur:",
            options=[
                ('number', 'Nombre'),
                ('string', 'Texte')
            ],
            initial_value=node.data.get('value_type', 'number'),
            on_change=on_type_change
        )
        layout.addWidget(type_frame)

        # Valeur - selon le type
        value_type = node.data.get('value_type', 'number')
        if value_type == 'string':
            val_frame, _ = create_text_field(
                container,
                label="Valeur:",
                initial_value=str(node.data.get('value', '')),
                on_change=node.widget.create_on_change_callback('value')
            )
        else:
            val_frame, _ = create_number_field(
                container,
                label="Valeur:",
                initial_value=float(node.data.get('value', 0)) if isinstance(node.data.get('value'), (int, float)) else 0,
                decimals=2,
                min_value=-999999,
                max_value=999999,
                on_change=node.widget.create_on_change_callback('value', transform=float)
            )
        layout.addWidget(val_frame)

        return container

    def _create_condition_editor(self, parent, node):
        """Éditeur pour un noeud condition"""
        # Créer un conteneur pour tous les champs
        from PyQt6.QtWidgets import QWidget, QVBoxLayout
        container = QWidget(parent)
        layout = QVBoxLayout()
        container.setLayout(layout)

        # Nom de la variable
        var_frame, _ = create_text_field(
            container,
            label="Variable:",
            initial_value=node.data.get('variable', 'score'),
            on_change=node.widget.create_on_change_callback('variable')
        )
        layout.addWidget(var_frame)

        # Opérateur
        op_frame, _ = create_dropdown_field(
            container,
            label="Opérateur:",
            options=['==', '!=', '>', '<', '>=', '<='],
            initial_value=node.data.get('operator', '=='),
            on_change=node.widget.create_on_change_callback('operator')
        )
        layout.addWidget(op_frame)

        # Valeur
        val_frame, _ = create_number_field(
            container,
            label="Valeur:",
            initial_value=node.data.get('value', 0),
            decimals=2,
            min_value=-999999,
            max_value=999999,
            on_change=node.widget.create_on_change_callback('value', transform=float)
        )
        layout.addWidget(val_frame)

        return container

    def validate(self, node_data: Dict[str, Any], graph_context: Dict[str, Any]) -> List[LintIssue]:
        """
        Valide un nœud de variable ou de condition.

        Vérifie:
        - Que le nom de variable n'est pas vide
        - Pour les opérations autres que 'set', que la variable est initialisée avant utilisation
        - Pour les conditions, que la variable testée existe
        """
        issues = []
        node_id = node_data.get('id', 'unknown')
        node_type = node_data.get('type', '')
        data = node_data.get('data', {})
        var_name = data.get('variable', '').strip()

        # Extraire le type simple
        simple_type = node_type.split('.')[-1] if '.' in node_type else node_type

        # Vérifier que le nom de variable n'est pas vide
        if not var_name:
            issues.append(LintIssue(
                node_id=node_id,
                severity=LintSeverity.ERROR,
                message="Variable name is empty",
                details=f"This {simple_type} node requires a valid variable name."
            ))
            return issues  # Pas besoin de vérifier plus si le nom est vide

        # Récupérer l'état de la mémoire
        memory_state = graph_context.get('memory_state', {})

        if simple_type == "variable":
            # Pour les opérations autres que 'set', vérifier que la variable existe
            operation = data.get('operation', 'set')
            value_type = data.get('value_type', 'number')

            # Vérifier les opérations incompatibles avec les strings
            if value_type == 'string' and operation in ['subtract', 'multiply']:
                issues.append(LintIssue(
                    node_id=node_id,
                    severity=LintSeverity.ERROR,
                    message=f"Operation '{operation}' not compatible with string type",
                    details=f"The operation '{operation}' cannot be used with string values. Only 'set' and 'add' (concatenation) are supported for strings."
                ))

            if operation in ['add', 'subtract', 'multiply']:
                if var_name not in memory_state:
                    issues.append(LintIssue(
                        node_id=node_id,
                        severity=LintSeverity.WARNING,
                        message=f"Variable '{var_name}' used in operation '{operation}' but never initialized",
                        details=f"The variable '{var_name}' is used with operation '{operation}' before being set. This may cause runtime errors or unexpected behavior."
                    ))

        elif simple_type == "condition":
            # Pour les conditions, vérifier que la variable testée existe
            if var_name not in memory_state:
                issues.append(LintIssue(
                    node_id=node_id,
                    severity=LintSeverity.WARNING,
                    message=f"Variable '{var_name}' used in condition but never initialized",
                    details=f"The variable '{var_name}' is tested in a condition before being set. This may cause unexpected behavior."
                ))

        return issues

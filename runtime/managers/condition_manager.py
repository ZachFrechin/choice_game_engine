"""
ConditionEvaluatorManager - Évalue les conditions et branche selon le résultat
"""

from typing import Dict, Any, Optional
from ..core.interfaces.node_manager_interface import INodeManager
from ..core.memory import Memory
from ..ui.gui import GUI


class ConditionEvaluatorManager(INodeManager):
    """
    Manager pour évaluer les conditions.

    Compare une variable avec une valeur selon un opérateur.
    Définit 'final_next' à 'output_true' ou 'output_false' selon le résultat.
    """

    @property
    def id(self) -> str:
        return "condition_evaluator"

    def process(self, node: Dict[str, Any], memory: Memory, gui: Optional[GUI] = None) -> Dict[str, Any]:
        """
        Évalue une condition et branche selon le résultat.

        Args:
            node: Node avec {'data': {'variable': '...', 'operator': '...', 'value': ...}}
            memory: Accès aux variables

        Returns:
            {'final_next': 'output_true'} ou {'final_next': 'output_false'}
        """
        data = node.get('data', {})
        variable = data.get('variable', 'var')
        operator = data.get('operator', '==')
        value = data.get('value', 0)

        # Évaluer la condition via Memory
        try:
            result = memory.compare(variable, operator, value)
        except ValueError as e:
            print(f"Erreur de condition: {e}")
            result = False

        # Debug: afficher la condition (optionnel)
        var_value = memory.get(variable, 0)
        # print(f"[Debug] {variable} ({var_value}) {operator} {value} = {result}")

        # Brancher selon le résultat
        # Note: Le creator sauvegarde les ports avec leurs IDs (output_true, output_false)
        if result:
            return {'final_next': 'output_true'}  # Port true
        else:
            return {'final_next': 'output_false'}  # Port false

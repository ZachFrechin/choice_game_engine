"""
VariableSetterManager - Modifie les variables dans la Memory
"""

from typing import Dict, Any, Optional
from ..core.interfaces.node_manager_interface import INodeManager
from ..core.memory import Memory
from ..ui.gui import GUI


class VariableSetterManager(INodeManager):
    """
    Manager pour manipuler les variables.

    Supporte les opérations: set, add, subtract, multiply
    Définit 'final_next' à 'output' pour continuer.
    """

    @property
    def id(self) -> str:
        return "variable_setter"

    def process(self, node: Dict[str, Any], memory: Memory, gui: Optional[GUI] = None) -> Dict[str, Any]:
        """
        Modifie une variable selon l'opération spécifiée.

        Args:
            node: Node avec {'data': {'variable': '...', 'operation': '...', 'value': ...}}
            memory: Accès aux variables

        Returns:
            {'final_next': 'output'}
        """
        data = node.get('data', {})
        variable = data.get('variable', 'var')
        operation = data.get('operation', 'set')
        value = data.get('value', 0)

        # Exécuter l'opération
        if operation == 'set':
            memory.set(variable, value)
        elif operation == 'add':
            memory.add(variable, value)
        elif operation == 'subtract':
            memory.subtract(variable, value)
        elif operation == 'multiply':
            memory.multiply(variable, value)
        else:
            print(f"Opération inconnue: {operation}")

        # Debug: afficher l'opération (optionnel)
        # print(f"[Debug] {variable} = {memory.get(variable)}")

        # Continuer au node suivant
        return {'final_next': 'output'}

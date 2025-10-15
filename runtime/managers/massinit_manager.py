"""
MassInitManager - Initialise plusieurs variables en une seule fois
"""

from typing import Dict, Any, Optional
from ..core.interfaces.node_manager_interface import INodeManager
from ..core.memory import Memory
from ..ui.gui import GUI


class MassInitManager(INodeManager):
    """
    Manager pour initialiser plusieurs variables simultanément.

    Lit une liste de {'name': '...', 'value': ...} et définit chaque variable.
    Définit 'final_next' à 'output' pour continuer.
    """

    @property
    def id(self) -> str:
        return "massinit"

    def process(self, node: Dict[str, Any], memory: Memory, gui: Optional[GUI] = None) -> Dict[str, Any]:
        """
        Initialise plusieurs variables.

        Args:
            node: Node avec {'data': {'variables': [{'name': '...', 'value': ...}, ...]}}
            memory: Accès aux variables

        Returns:
            {'final_next': 'output'}
        """
        data = node.get('data', {})
        variables = data.get('variables', [])

        # Définir chaque variable
        for var in variables:
            name = var.get('name', '')
            value = var.get('value', 0)

            if name:  # Seulement si le nom n'est pas vide
                memory.set(name, value)

        # Continuer au node suivant
        return {'final_next': 'output'}

"""
Register - Association entre types de nodes et NodeManagers

Le Register maintient une map de quel(s) manager(s) doivent traiter chaque type de node.
"""

from typing import Dict, List
from .interfaces.node_manager_interface import INodeManager


class Register:
    """
    Registre des NodeManagers par type de node.

    Permet d'associer un ou plusieurs managers à chaque type de node.
    Format: node_type → [manager1, manager2, ...]
    """

    def __init__(self):
        # Map: type de node → liste de managers
        self._registry: Dict[str, List[INodeManager]] = {}

        # Map: manager_id → manager (pour éviter les doublons)
        self._managers: Dict[str, INodeManager] = {}

    def register_manager(self, node_type: str, manager: INodeManager) -> None:
        """
        Enregistre un manager pour un type de node.

        Args:
            node_type: Type de node (ex: 'text.text', 'choice.choice')
            manager: Instance du NodeManager

        Un même manager peut être enregistré pour plusieurs types de nodes.
        Un même type de node peut avoir plusieurs managers (exécutés dans l'ordre).
        """
        # Stocker le manager si nouveau
        if manager.id not in self._managers:
            self._managers[manager.id] = manager

        # Ajouter à la liste des managers pour ce type
        if node_type not in self._registry:
            self._registry[node_type] = []

        # Éviter les doublons
        if manager not in self._registry[node_type]:
            self._registry[node_type].append(manager)

    def unregister_manager(self, node_type: str, manager_id: str) -> bool:
        """
        Retire un manager d'un type de node.

        Args:
            node_type: Type de node
            manager_id: ID du manager à retirer

        Returns:
            True si le manager a été retiré, False sinon
        """
        if node_type not in self._registry:
            return False

        managers = self._registry[node_type]
        for manager in managers:
            if manager.id == manager_id:
                managers.remove(manager)
                return True

        return False

    def get_managers(self, node_type: str) -> List[INodeManager]:
        """
        Récupère la liste des managers pour un type de node.

        Args:
            node_type: Type de node

        Returns:
            Liste des managers (vide si aucun)
        """
        return self._registry.get(node_type, [])

    def has_managers(self, node_type: str) -> bool:
        """
        Vérifie si un type de node a des managers enregistrés.

        Args:
            node_type: Type de node

        Returns:
            True si au moins un manager est enregistré
        """
        return node_type in self._registry and len(self._registry[node_type]) > 0

    def get_all_managers(self) -> Dict[str, INodeManager]:
        """
        Retourne tous les managers enregistrés.

        Returns:
            Dict {manager_id: manager}
        """
        return dict(self._managers)

    def get_registered_types(self) -> List[str]:
        """
        Retourne tous les types de nodes enregistrés.

        Returns:
            Liste des types de nodes
        """
        return list(self._registry.keys())

    def clear(self) -> None:
        """Vide le registre."""
        self._registry.clear()
        self._managers.clear()

    def __repr__(self) -> str:
        return f"Register({len(self._registry)} node types, {len(self._managers)} managers)"

    def __str__(self) -> str:
        lines = ["Register:"]
        for node_type, managers in self._registry.items():
            manager_ids = [m.id for m in managers]
            lines.append(f"  {node_type} → {manager_ids}")
        return "\n".join(lines)

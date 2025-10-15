"""
Transitioner - Gère les transitions entre nodes

Le Transitioner vérifie qu'un node a été correctement traité (possède 'final_next')
et trouve le node suivant via les connexions.
"""

from typing import Dict, List, Any, Optional


class TransitionError(Exception):
    """Erreur lors d'une transition."""
    pass


class Transitioner:
    """
    Gère les transitions entre nodes.

    Vérifie que chaque node a défini 'final_next' avant de passer au suivant.
    Trouve le node cible via les connexions du template.
    """

    def __init__(self, connections: List[Dict[str, Any]]):
        """
        Initialise le Transitioner.

        Args:
            connections: Liste des connexions du template
                Format: [{'from_node': 'id1', 'from_port': 'output', 'to_node': 'id2'}, ...]
        """
        self.connections = connections

    def validate_transition(self, node: Dict[str, Any], result: Dict[str, Any]) -> None:
        """
        Valide qu'un node peut transitionner.

        Args:
            node: Node source
            result: Résultat du traitement par les managers

        Raises:
            TransitionError: Si 'final_next' n'est pas défini
        """
        if 'final_next' not in result:
            raise TransitionError(
                f"Node '{node.get('id', 'unknown')}' (type: {node.get('type', 'unknown')}) "
                f"was not properly processed: 'final_next' is missing. "
                f"Make sure at least one NodeManager sets 'final_next'."
            )

    def get_next_node(self, current_node_id: str, output_port: str) -> Optional[str]:
        """
        Trouve le node suivant via les connexions.

        Args:
            current_node_id: ID du node actuel
            output_port: Port de sortie (ex: 'output', 'output_0')

        Returns:
            ID du node suivant ou None si pas de connexion
        """
        # Chercher une correspondance exacte d'abord
        for conn in self.connections:
            if conn['from_node'] == current_node_id and conn['from_port'] == output_port:
                return conn['to_node']

        # Si pas trouvé et que le port est simple (ex: 'output'), essayer avec '_0'
        # Car le creator sauvegarde 'output_0' mais les managers retournent souvent 'output'
        if '_' not in output_port:
            indexed_port = f"{output_port}_0"
            for conn in self.connections:
                if conn['from_node'] == current_node_id and conn['from_port'] == indexed_port:
                    return conn['to_node']

        # Aucune connexion trouvée
        return None

    def transition(self, node: Dict[str, Any], result: Dict[str, Any]) -> Optional[str]:
        """
        Effectue une transition complète : validation + recherche du node suivant.

        Args:
            node: Node source
            result: Résultat du traitement

        Returns:
            ID du node suivant ou None (fin du jeu)

        Raises:
            TransitionError: Si la transition est invalide
        """
        # Valider que le node a été correctement traité
        self.validate_transition(node, result)

        # Récupérer le port de sortie
        output_port = result['final_next']

        # Trouver le node suivant
        next_node_id = self.get_next_node(node['id'], output_port)

        return next_node_id

    def has_connection(self, node_id: str, output_port: str) -> bool:
        """
        Vérifie si une connexion existe pour un node et port donnés.

        Args:
            node_id: ID du node
            output_port: Port de sortie

        Returns:
            True si une connexion existe
        """
        return self.get_next_node(node_id, output_port) is not None

    def get_connections_from(self, node_id: str) -> List[Dict[str, Any]]:
        """
        Récupère toutes les connexions partant d'un node.

        Args:
            node_id: ID du node

        Returns:
            Liste des connexions
        """
        return [conn for conn in self.connections if conn['from_node'] == node_id]

    def get_connections_to(self, node_id: str) -> List[Dict[str, Any]]:
        """
        Récupère toutes les connexions arrivant à un node.

        Args:
            node_id: ID du node

        Returns:
            Liste des connexions
        """
        return [conn for conn in self.connections if conn['to_node'] == node_id]

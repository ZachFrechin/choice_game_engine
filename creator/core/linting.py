"""
Système de linting pour le créator.
Permet aux nœuds de définir leurs propres validations.
"""

from typing import Protocol, List, Dict, Any, Optional, Tuple
from enum import Enum


class LintSeverity(Enum):
    """Niveau de sévérité d'un problème de linting."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class LintIssue:
    """Représente un problème détecté par le linter."""

    def __init__(
        self,
        node_id: str,
        severity: LintSeverity,
        message: str,
        details: Optional[str] = None
    ):
        self.node_id = node_id
        self.severity = severity
        self.message = message
        self.details = details

    def __repr__(self) -> str:
        return f"LintIssue({self.severity.value}: {self.message} @ {self.node_id})"


class ILintable(Protocol):
    """
    Interface pour les nœuds qui peuvent être validés par le linter.

    Les modules doivent implémenter la méthode validate() pour définir
    leurs propres règles de validation.
    """

    def validate(self, node_data: Dict[str, Any], graph_context: Dict[str, Any]) -> List[LintIssue]:
        """
        Valide un nœud et retourne une liste de problèmes détectés.

        Args:
            node_data: Données du nœud à valider (id, type, data, etc.)
            graph_context: Contexte du graphe complet (tous les nœuds, connexions, memory state, etc.)

        Returns:
            Liste de LintIssue détectés (vide si aucun problème)

        Exemple d'implémentation:
            def validate(self, node_data, graph_context):
                issues = []
                var_name = node_data.get('data', {}).get('variable_name')

                if not var_name:
                    issues.append(LintIssue(
                        node_id=node_data['id'],
                        severity=LintSeverity.ERROR,
                        message="Variable name is required",
                        details="This node requires a variable name to function properly."
                    ))

                # Vérifier si la variable existe dans le contexte
                memory_state = graph_context.get('memory_state', {})
                if var_name and var_name not in memory_state:
                    issues.append(LintIssue(
                        node_id=node_data['id'],
                        severity=LintSeverity.WARNING,
                        message=f"Variable '{var_name}' is not initialized",
                        details="This variable is used before being set."
                    ))

                return issues
        """
        ...


class LintEngine:
    """
    Moteur de linting qui parcourt le graphe et collecte tous les problèmes.
    """

    def __init__(self):
        self.modules: Dict[str, Any] = {}  # node_type -> module instance

    def register_module(self, node_type: str, module: Any):
        """Enregistre un module pour un type de nœud."""
        self.modules[node_type] = module

    def lint_graph(self, graph_data: Dict[str, Any]) -> List[LintIssue]:
        """
        Analyse un graphe complet et retourne tous les problèmes détectés.

        Args:
            graph_data: Dictionnaire contenant 'nodes', 'connections', etc.

        Returns:
            Liste de tous les LintIssue trouvés
        """
        all_issues: List[LintIssue] = []

        # Construire le contexte du graphe (qui convertit nodes en liste si nécessaire)
        graph_context = self._build_graph_context(graph_data)

        # Récupérer la liste de nodes depuis le contexte
        nodes = graph_context.get('nodes', [])

        # Validation générique: vérifier qu'un port n'a qu'une seule connexion
        port_validation_issues = self._validate_port_connections(graph_context)
        all_issues.extend(port_validation_issues)

        # Valider chaque nœud
        for node in nodes:
            node_type = node.get('type')
            module = self.modules.get(node_type)

            # Vérifier si le module implémente ILintable
            if module and hasattr(module, 'validate') and callable(module.validate):
                try:
                    issues = module.validate(node, graph_context)
                    all_issues.extend(issues)
                except Exception as e:
                    # Si la validation plante, créer une erreur
                    all_issues.append(LintIssue(
                        node_id=node.get('id', 'unknown'),
                        severity=LintSeverity.ERROR,
                        message=f"Validation failed: {str(e)}",
                        details=f"Error in {node_type} validation"
                    ))

        return all_issues

    def _validate_port_connections(self, graph_context: Dict[str, Any]) -> List[LintIssue]:
        """
        Valide que chaque port de SORTIE n'a qu'une seule connexion.

        Règle: Un port de sortie ne peut être connecté qu'à un seul port.
        Les ports d'entrée peuvent avoir plusieurs connexions.
        """
        issues = []
        connections = graph_context.get('connections', [])

        # Compter les connexions par port de SORTIE uniquement
        # Format: {(node_id, port_id): count}
        output_port_connections = {}

        for conn in connections:
            from_node = conn.get('from_node')
            from_port = conn.get('from_port')

            # Compter uniquement les ports de sortie
            key = (from_node, from_port)
            output_port_connections[key] = output_port_connections.get(key, 0) + 1

        # Vérifier les ports de sortie avec plusieurs connexions
        for (node_id, port_id), count in output_port_connections.items():
            if count > 1:
                issues.append(LintIssue(
                    node_id=node_id,
                    severity=LintSeverity.ERROR,
                    message=f"Output port '{port_id}' has {count} connections",
                    details=f"The output port '{port_id}' is connected to {count} different ports. Each output port can only have one connection."
                ))

        return issues

    def _build_graph_context(self, graph_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construit le contexte du graphe pour les validations.

        Analyse le graphe pour extraire:
        - Les variables initialisées
        - Les connexions entre nœuds
        - L'ordre d'exécution probable
        - etc.
        """
        # Les nodes peuvent être un dict ou une liste
        nodes_data = graph_data.get('nodes', {})
        if isinstance(nodes_data, dict):
            # Convertir le dict en liste
            nodes = [
                {
                    'id': node_id,
                    'type': node_info.get('type'),
                    'data': node_info.get('data', {}),
                    'x': node_info.get('x', 0),
                    'y': node_info.get('y', 0)
                }
                for node_id, node_info in nodes_data.items()
            ]
        else:
            nodes = nodes_data

        connections = graph_data.get('connections', [])

        # Simuler l'état de la mémoire en parcourant le graphe
        memory_state = {}

        # Trouver le nœud de départ
        start_nodes = [n for n in nodes if n.get('type') == 'flow.start']

        if start_nodes:
            # Parcourir le graphe depuis le start
            visited = set()
            self._traverse_and_collect_memory(
                start_nodes[0]['id'],
                nodes,
                connections,
                memory_state,
                visited
            )
        else:
            # Pas de nœud start, analyser toutes les variables 'set' disponibles
            # pour donner une approximation de l'état de la mémoire
            for node in nodes:
                node_type = node.get('type')

                if node_type == 'variables.variable':
                    operation = node.get('data', {}).get('operation', 'set')
                    if operation == 'set':
                        var_name = node.get('data', {}).get('variable')
                        if var_name:
                            memory_state[var_name] = True

                elif node_type == 'massinit.massinit':
                    variables = node.get('data', {}).get('variables', [])
                    for var in variables:
                        var_name = var.get('name')
                        if var_name:
                            memory_state[var_name] = True

        return {
            'nodes': nodes,
            'connections': connections,
            'memory_state': memory_state,
            'node_by_id': {n['id']: n for n in nodes},
        }

    def _traverse_and_collect_memory(
        self,
        node_id: str,
        nodes: List[Dict],
        connections: List[Dict],
        memory_state: Dict[str, Any],
        visited: set
    ):
        """
        Parcourt le graphe et collecte les variables initialisées.
        """
        if node_id in visited:
            return

        visited.add(node_id)

        # Trouver le nœud
        node = next((n for n in nodes if n['id'] == node_id), None)
        if not node:
            return

        # Si c'est un nœud de variable qui SET, l'ajouter à memory_state
        node_type = node.get('type', '')
        node_data = node.get('data', {})

        # Vérifier si c'est un nœud de variable avec opération 'set'
        if node_type == 'variables.variable':
            operation = node_data.get('operation', 'set')
            if operation == 'set':
                var_name = node_data.get('variable')
                if var_name:
                    memory_state[var_name] = True  # Marquer comme initialisée

        # Vérifier si c'est un nœud MassInit
        elif node_type == 'massinit.massinit':
            variables = node_data.get('variables', [])
            for var in variables:
                var_name = var.get('name')
                if var_name:
                    memory_state[var_name] = True  # Marquer comme initialisée

        # Trouver les connexions sortantes
        outgoing = [c for c in connections if c.get('from_node') == node_id]

        for conn in outgoing:
            target_id = conn.get('to_node')
            if target_id:
                self._traverse_and_collect_memory(
                    target_id, nodes, connections, memory_state, visited
                )

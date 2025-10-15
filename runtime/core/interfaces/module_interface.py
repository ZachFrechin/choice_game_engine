"""
Interface pour les modules runtime

Architecture:
-------------
Le moteur (core) est GÉNÉRIQUE et ne connaît AUCUN type de nœud spécifique.
Les modules runtime définissent comment EXÉCUTER chaque type de nœud.

Correspondance Creator ↔ Runtime:
----------------------------------
Creator Module (IModule)          →    Runtime Module (IRuntimeModule)
  - create_node_widget()                 - execute_node()
  - get_node_types()                     - get_supported_nodes()
  - create_properties_editor()           - handle_user_input()

Exemple:
--------
# Module Text
class TextRuntimeModule(IRuntimeModule):
    def execute_node(self, node_data, context):
        # Afficher le texte
        text = node_data['content']
        print(text)
        return {'next': 'output'}  # Continuer vers le port 'output'
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class IRuntimeModule(ABC):
    """Interface pour les modules d'exécution"""

    @property
    @abstractmethod
    def id(self) -> str:
        """ID du module (doit correspondre au module creator)"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Nom du module"""
        pass

    @abstractmethod
    def get_supported_nodes(self) -> List[str]:
        """
        Liste des types de nœuds supportés par ce module

        Returns:
            Liste des type_id (ex: ['text', 'choice'])
        """
        pass

    @abstractmethod
    def execute_node(self, node_data: Dict[str, Any], context: 'GameContext') -> Dict[str, Any]:
        """
        Exécute un nœud et retourne le résultat

        Args:
            node_data: Données du nœud (type, data, etc.)
            context: Contexte du jeu (variables, état, etc.)

        Returns:
            Dict avec:
            - 'next': ID du port de sortie à suivre (ex: 'output', 'output_0')
            - 'wait_input': bool, si True attend une entrée utilisateur
            - autres données spécifiques au module
        """
        pass

    def initialize(self, context: 'GameContext') -> None:
        """Initialise le module (optionnel)"""
        pass

    def cleanup(self, context: 'GameContext') -> None:
        """Nettoie les ressources (optionnel)"""
        pass


class GameContext:
    """
    Contexte d'exécution du jeu

    Contient:
    - Variables du jeu
    - Historique des nœuds visités
    - État actuel
    """

    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.history: List[str] = []
        self.current_node: Optional[str] = None
        self.custom_data: Dict[str, Any] = {}

    def set_variable(self, name: str, value: Any):
        """Définit une variable"""
        self.variables[name] = value

    def get_variable(self, name: str, default: Any = None) -> Any:
        """Récupère une variable"""
        return self.variables.get(name, default)

    def add_to_history(self, node_id: str):
        """Ajoute un nœud à l'historique"""
        self.history.append(node_id)

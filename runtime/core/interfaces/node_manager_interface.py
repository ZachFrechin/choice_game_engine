"""
Interface pour les NodeManagers

Un NodeManager est responsable de traiter/transformer un node avant son passage au suivant.
Chaque node peut passer par plusieurs managers selon sa configuration dans le Register.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class INodeManager(ABC):
    """
    Interface pour les managers de nodes.

    Un NodeManager reçoit un node, le traite, et peut :
    - Afficher du contenu
    - Modifier les données du node
    - Interagir avec l'utilisateur
    - Accéder à la Memory
    - Définir final_next pour indiquer le port de sortie
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """
        Identifiant unique du manager.

        Returns:
            str: ID du manager (ex: 'text_display', 'variable_setter')
        """
        pass

    @abstractmethod
    def process(self, node: Dict[str, Any], memory: 'Memory', gui: 'GUI' = None) -> Dict[str, Any]:
        """
        Traite un node.

        Args:
            node: Données complètes du node
                  {'id': '...', 'type': 'text.text', 'data': {...}}
            memory: Accès au système de variables
            gui: Accès au moteur GUI (optionnel)

        Returns:
            Dict avec modifications au node, doit inclure 'final_next' si c'est le dernier manager
            Exemple: {'final_next': 'output'} ou {'final_next': 'output_1'}

        Le node peut être modifié directement ou retourner un dict de modifications.
        Le Transitioner vérifiera que 'final_next' est défini avant de continuer.
        """
        pass

    def initialize(self, memory: 'Memory', gui: 'GUI' = None) -> None:
        """
        Initialisation du manager (optionnel).
        Appelé une fois au démarrage du moteur.

        Args:
            memory: Accès au système de variables
            gui: Accès au moteur GUI (optionnel)
        """
        pass

    def cleanup(self, memory: 'Memory', gui: 'GUI' = None) -> None:
        """
        Nettoyage du manager (optionnel).
        Appelé à la fin du jeu.

        Args:
            memory: Accès au système de variables
            gui: Accès au moteur GUI (optionnel)
        """
        pass

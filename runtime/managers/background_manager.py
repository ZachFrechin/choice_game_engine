"""
BackgroundManager - Affiche une image de fond

Gère l'affichage d'une image d'arrière-plan via le composant background_image.
"""

from typing import Dict, Any, Optional
from ..core.interfaces.node_manager_interface import INodeManager
from ..core.memory import Memory
from ..ui.gui import GUI


class BackgroundManager(INodeManager):
    """
    Manager pour les nodes background.

    Affiche une image d'arrière-plan en utilisant le composant background_image du GUI.
    """

    @property
    def id(self) -> str:
        return "background_manager"

    def initialize(self, memory: Memory, gui: Optional[GUI] = None) -> None:
        """Initialisation du manager"""
        pass

    def process(self, node: Dict[str, Any], memory: Memory, gui: Optional[GUI] = None) -> Dict[str, Any]:
        """
        Traite un node background.

        Args:
            node: Node avec image_path
            memory: Mémoire du jeu
            gui: Interface graphique

        Returns:
            Dictionnaire avec final_next
        """
        if not gui:
            print("⚠️  GUI non disponible, impossible d'afficher le background")
            return {'final_next': 'output'}

        # Récupérer le chemin de l'image
        image_path = node.get('data', {}).get('image_path', '')

        if not image_path:
            print("⚠️  Aucun chemin d'image spécifié")
            return {'final_next': 'output'}

        # Afficher l'image de fond
        gui.show_component('background_image', image_path=image_path)

        # Retourner le next par défaut
        return {'final_next': 'output'}

    def cleanup(self, memory: Memory, gui: Optional[GUI] = None) -> None:
        """Nettoyage du manager"""
        # Le background reste affiché, pas besoin de le cacher
        pass

    def validate_node(self, node: Dict[str, Any]) -> bool:
        """
        Valide qu'un node background est correct.

        Args:
            node: Node à valider

        Returns:
            True si valide
        """
        data = node.get('data', {})

        # Vérifier que image_path existe
        if 'image_path' not in data:
            return False

        return True

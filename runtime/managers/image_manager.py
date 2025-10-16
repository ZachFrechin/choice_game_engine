"""
ImageManager - Affiche une image avec système de layers

Gère l'affichage d'images via le composant image avec support multi-layers.
"""

from typing import Dict, Any, Optional
from ..core.interfaces.node_manager_interface import INodeManager
from ..core.memory import Memory
from ..ui.gui import GUI


class ImageManager(INodeManager):
    """
    Manager pour les nodes image.

    Affiche une image en utilisant le composant image du GUI avec système de layers.
    """

    @property
    def id(self) -> str:
        return "image_manager"

    def initialize(self, memory: Memory, gui: Optional[GUI] = None) -> None:
        """Initialisation du manager"""
        pass

    def process(self, node: Dict[str, Any], memory: Memory, gui: Optional[GUI] = None) -> Dict[str, Any]:
        """
        Traite un node image.

        Args:
            node: Node avec image_path et layer
            memory: Mémoire du jeu
            gui: Interface graphique

        Returns:
            Dictionnaire avec final_next
        """
        if not gui:
            print("⚠️  GUI non disponible, impossible d'afficher l'image")
            return {'final_next': 'output'}

        # Récupérer le chemin de l'image et le layer
        data = node.get('data', {})
        image_path = data.get('image_path', '')
        layer = data.get('layer', 0)

        if not image_path:
            print("⚠️  Aucun chemin d'image spécifié")
            return {'final_next': 'output'}

        # Afficher l'image sur le layer spécifié
        gui.show_component('image', image_path=image_path, layer=layer)

        # Retourner le next par défaut
        return {'final_next': 'output'}

    def cleanup(self, memory: Memory, gui: Optional[GUI] = None) -> None:
        """Nettoyage du manager"""
        # Les images restent affichées, pas besoin de les cacher
        pass

    def validate_node(self, node: Dict[str, Any]) -> bool:
        """
        Valide qu'un node image est correct.

        Args:
            node: Node à valider

        Returns:
            True si valide
        """
        data = node.get('data', {})

        # Vérifier que image_path existe
        if 'image_path' not in data:
            return False

        # Vérifier que layer existe (optionnel, défaut à 0)
        if 'layer' not in data:
            data['layer'] = 0

        return True

"""
MusicManager - Joue de la musique de fond

Gère la lecture de musique via le composant music du GUI.
"""

from typing import Dict, Any, Optional
from ..core.interfaces.node_manager_interface import INodeManager
from ..core.memory import Memory
from ..ui.gui import GUI


class MusicManager(INodeManager):
    """
    Manager pour les nodes de musique.

    Joue de la musique de fond en utilisant le composant music du GUI.
    """

    @property
    def id(self) -> str:
        return "music_manager"

    def initialize(self, memory: Memory, gui: Optional[GUI] = None) -> None:
        """Initialisation du manager"""
        pass

    def process(self, node: Dict[str, Any], memory: Memory, gui: Optional[GUI] = None) -> Dict[str, Any]:
        """
        Traite un node music.

        Args:
            node: Node avec music_path
            memory: Mémoire du jeu
            gui: Interface graphique

        Returns:
            Dictionnaire avec final_next
        """
        if not gui:
            print("⚠️  GUI non disponible, impossible de jouer la musique")
            return {'final_next': 'output'}

        # Récupérer le chemin du fichier audio
        music_path = node.get('data', {}).get('music_path', '')

        if not music_path:
            print("⚠️  Aucun chemin de musique spécifié")
            return {'final_next': 'output'}

        # Jouer la musique
        gui.show_component('music', music_path=music_path)

        # Retourner le next par défaut
        return {'final_next': 'output'}

    def cleanup(self, memory: Memory, gui: Optional[GUI] = None) -> None:
        """Nettoyage du manager"""
        # La musique continue à jouer, pas besoin de l'arrêter
        pass

    def validate_node(self, node: Dict[str, Any]) -> bool:
        """
        Valide qu'un node music est correct.

        Args:
            node: Node à valider

        Returns:
            True si valide
        """
        data = node.get('data', {})

        # Vérifier que music_path existe
        if 'music_path' not in data:
            return False

        return True

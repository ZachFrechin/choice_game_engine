"""
MusicManager - Joue de la musique avec système de pistes

Gère la lecture de musique via le composant music du GUI avec support multi-pistes et repeat.
"""

from typing import Dict, Any, Optional
from ..core.interfaces.node_manager_interface import INodeManager
from ..core.memory import Memory
from ..ui.gui import GUI


class MusicManager(INodeManager):
    """
    Manager pour les nodes de musique.

    Joue de la musique en utilisant le composant music du GUI avec système de pistes et option repeat.
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
            node: Node avec music_path, track et repeat
            memory: Mémoire du jeu
            gui: Interface graphique

        Returns:
            Dictionnaire avec final_next
        """
        if not gui:
            print("⚠️  GUI non disponible, impossible de jouer la musique")
            return {'final_next': 'output'}

        # Récupérer les données du node
        data = node.get('data', {})
        music_path = data.get('music_path', '')
        track = data.get('track', 0)
        repeat = data.get('repeat', True)

        if not music_path:
            print("⚠️  Aucun chemin de musique spécifié")
            return {'final_next': 'output'}

        # Jouer la musique sur la piste spécifiée avec le mode repeat
        gui.show_component('music', music_path=music_path, track=track, repeat=repeat)

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

        # Vérifier que track existe (optionnel, défaut à 0)
        if 'track' not in data:
            data['track'] = 0

        # Vérifier que repeat existe (optionnel, défaut à True)
        if 'repeat' not in data:
            data['repeat'] = True

        return True

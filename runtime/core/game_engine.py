"""
Game Engine - Moteur générique d'exécution avec architecture NodeManager

Architecture:
1. Load template (nodes + connections)
2. For each node:
   - Get managers from Register
   - Execute managers in order (pass node + memory)
   - Validate that 'final_next' is set
   - Use Transitioner to find next node
3. Repeat until no next node
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from .memory import Memory
from .register import Register
from .transitioner import Transitioner, TransitionError
from .interfaces.node_manager_interface import INodeManager
from .saver import Saver, SaveData
from .key_handler import KeyHandler
from ..ui.gui import GUI


class ReturnToMenuException(Exception):
    """Exception levée pour retourner au menu principal."""
    pass


class GameEngine:
    """
    Moteur générique d'exécution de jeu basé sur NodeManagers.

    Le moteur est complètement générique et ne connaît aucun type de node.
    Toute la logique est déléguée aux NodeManagers enregistrés dans le Register.
    """

    def __init__(self, save_directory: Optional[Path] = None):
        self.memory = Memory()
        self.register = Register()
        self.key_handler = KeyHandler()
        self.gui = GUI(key_handler=self.key_handler, scroll_callback=self._handle_scroll_back, engine=self)
        self.saver = Saver(save_directory)
        self.transitioner: Optional[Transitioner] = None

        self.template: Optional[Dict[str, Any]] = None
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.start_node: Optional[str] = None
        self.current_node: Optional[str] = None

        # Historique d'exécution avec snapshots de mémoire
        self.history: List[str] = []
        self.memory_snapshots: List[Dict[str, Any]] = []  # Snapshot de la mémoire à chaque node
        self.can_go_back: bool = False
        self._go_back_requested: bool = False  # Flag pour demander un retour en arrière

    # ==================== Enregistrement des managers ====================

    def register_manager(self, node_type: str, manager: INodeManager) -> None:
        """
        Enregistre un NodeManager pour un type de node.

        Args:
            node_type: Type de node (ex: 'text.text')
            manager: Instance du NodeManager
        """
        self.register.register_manager(node_type, manager)

    def register_manager_for_multiple(self, node_types: List[str], manager: INodeManager) -> None:
        """
        Enregistre un NodeManager pour plusieurs types de nodes.

        Args:
            node_types: Liste de types de nodes
            manager: Instance du NodeManager
        """
        for node_type in node_types:
            self.register.register_manager(node_type, manager)

    def initialize_managers(self) -> None:
        """Initialise tous les managers enregistrés et le GUI."""
        # Initialiser le GUI
        self.gui.initialize()

        # Initialiser les managers
        for manager in self.register.get_all_managers().values():
            manager.initialize(self.memory, self.gui)

    def cleanup_managers(self) -> None:
        """Nettoie tous les managers et le GUI."""
        # Nettoyer les managers
        for manager in self.register.get_all_managers().values():
            manager.cleanup(self.memory, self.gui)

        # Nettoyer le GUI
        self.gui.cleanup()

    # ==================== Chargement du template ====================

    def load_template(self, template_path: Path) -> None:
        """
        Charge une template depuis un fichier JSON.

        Args:
            template_path: Chemin vers le fichier template
        """
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template = json.load(f)

        # Résoudre les chemins relatifs par rapport au dossier du projet
        self._resolve_asset_paths(template_path.parent)

        # Charger les nodes
        self.nodes = self.template.get('nodes', {})

        # Charger les connexions et créer le Transitioner
        connections = self.template.get('connections', [])
        self.transitioner = Transitioner(connections)

        # Trouver le node de départ
        self.start_node = self.template.get('start_node')
        if not self.start_node and self.nodes:
            self.start_node = list(self.nodes.keys())[0]

        print(f"✓ Template chargée: {template_path.name}")
        print(f"  Nœuds: {len(self.nodes)}")
        print(f"  Connexions: {len(connections)}\n")

    def _resolve_asset_paths(self, project_dir: Path) -> None:
        """
        Résout les chemins relatifs des assets par rapport au dossier du projet.

        Args:
            project_dir: Dossier du projet (où se trouve le fichier template)
        """
        # Champs qui contiennent des chemins de fichiers
        path_fields = ['image_path', 'music_path', 'character_image']

        # Parcourir tous les nodes
        for node_id, node_data in self.template.get('nodes', {}).items():
            data = node_data.get('data', {})

            for field in path_fields:
                if field in data and data[field]:
                    path = Path(data[field])
                    if not path.is_absolute():
                        # Convertir en chemin absolu par rapport au projet
                        abs_path = (project_dir / path).resolve()
                        data[field] = str(abs_path)

    # ==================== Exécution ====================

    def process_node(self, node_id: str) -> Dict[str, Any]:
        """
        Traite un node en le faisant passer par tous ses managers.

        Args:
            node_id: ID du node à traiter

        Returns:
            Résultat du traitement (doit contenir 'final_next')

        Raises:
            ValueError: Si le node n'existe pas
            KeyError: Si aucun manager n'est enregistré pour ce type de node
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node '{node_id}' not found")

        node = self.nodes[node_id]
        node_type = node.get('type')

        # Récupérer les managers pour ce type
        managers = self.register.get_managers(node_type)
        if not managers:
            raise KeyError(
                f"No managers registered for node type '{node_type}'. "
                f"Register at least one manager for this type."
            )

        # Faire passer le node par tous les managers
        result = {}
        for manager in managers:
            manager_result = manager.process(node, self.memory, self.gui)
            if manager_result:
                result.update(manager_result)

        # Ajouter à l'historique seulement si le manager le demande
        # (typiquement pour les nodes qui attendent une interaction utilisateur)
        if result.get('add_to_history', False):
            self.history.append(node_id)

        return result

    def run(self, start_node: Optional[str] = None) -> None:
        """
        Exécute le jeu en démarrant par le menu principal.

        Args:
            start_node: ID du node de départ (ignoré si menu affiché)
        """
        if not self.template:
            print("Erreur: Aucune template chargée")
            return

        if not self.transitioner:
            print("Erreur: Transitioner non initialisé")
            return

        # Initialiser les managers et le GUI
        self.initialize_managers()

        print("=" * 50)
        print("DÉMARRAGE DU JEU")
        print("=" * 50)

        try:
            # Boucle principale : menu -> jeu -> retour menu
            while True:
                # Afficher le menu principal
                menu_action = self.gui.show_component('game_menu')

                if menu_action == 'quit':
                    print("Fermeture du jeu...")
                    break
                elif menu_action == 'load':
                    # Afficher un menu de sélection de slot (pour l'instant slot 1)
                    if not self.load_game(slot=1):
                        print("Démarrage d'une nouvelle partie...")
                        self.current_node = start_node or self.start_node
                    # Sinon current_node est défini par load_game
                else:  # 'new'
                    print("Nouvelle partie...")
                    self.current_node = start_node or self.start_node

                # Réinitialiser l'état pour la nouvelle partie
                self.history.clear()
                self.memory_snapshots.clear()
                self.can_go_back = False

                # Cacher tous les composants GUI (musique, background, etc.)
                self.gui.hide_all_components()

                if menu_action == 'new':
                    # Réinitialiser la mémoire seulement pour une nouvelle partie
                    self.memory.clear()

                # Lancer la boucle de jeu
                try:
                    self._game_loop()

                    # À la fin du jeu, afficher un message et revenir au menu
                    print("\n" + "=" * 50)
                    print("FIN DE LA PARTIE")
                    print("=" * 50 + "\n")
                except ReturnToMenuException:
                    # Retour au menu demandé
                    print("\n⏸️  Retour au menu principal")
                    # Cacher tous les composants avant de retourner au menu
                    self.gui.hide_all_components()
                    continue

        except KeyboardInterrupt:
            print("\n\n⏸️  Jeu interrompu")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("\n" + "=" * 50)
            print("FIN DU JEU")
            print("=" * 50)

            # Nettoyer les managers
            self.cleanup_managers()

    def _game_loop(self) -> None:
        """Boucle principale du jeu (traitement des nodes)."""
        import time
        current = self.current_node

        while current:
            # Process events pour permettre au scroll d'être détecté
            self.gui.process_events()
            time.sleep(0.01)

            # Vérifier si un retour en arrière est demandé
            if self._go_back_requested:
                self._go_back_requested = False
                if self.go_back():
                    current = self.current_node
                    continue
                else:
                    # Impossible de revenir en arrière, continuer normalement
                    pass

            self.current_node = current

            # Sauvegarder un snapshot de la mémoire AVANT de traiter le node
            self.memory_snapshots.append(self.memory.get_all().copy())
            self.can_go_back = len(self.history) > 0

            # Traiter le node via ses managers
            result = self.process_node(current)

            # Valider et transitionner
            try:
                next_node = self.transitioner.transition(self.nodes[current], result)
                current = next_node
            except TransitionError as e:
                print(f"\n❌ Erreur de transition: {e}")
                break

    def _handle_scroll_back(self) -> None:
        """Callback appelé quand l'utilisateur scroll vers le haut."""
        if self.can_go_back:
            self._go_back_requested = True

    def return_to_menu(self) -> None:
        """Lève une exception pour retourner au menu principal."""
        raise ReturnToMenuException()

    # ==================== Utilitaires ====================

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un node par son ID."""
        return self.nodes.get(node_id)

    def get_history(self) -> List[str]:
        """Retourne l'historique des nodes visités."""
        return list(self.history)

    def clear_history(self) -> None:
        """Vide l'historique."""
        self.history.clear()
        self.memory_snapshots.clear()
        self.can_go_back = False

    def go_back(self) -> bool:
        """
        Retourne au node précédent dans l'historique.

        Returns:
            True si le retour en arrière a réussi, False sinon
        """
        if len(self.history) < 1:
            return False

        # Retirer le node actuel de l'historique
        self.history.pop()
        if self.memory_snapshots:
            self.memory_snapshots.pop()

        if not self.history:
            return False

        # Récupérer le node précédent
        previous_node = self.history[-1]
        previous_memory = self.memory_snapshots[-1] if self.memory_snapshots else {}

        # Restaurer l'état
        self.current_node = previous_node
        self.memory.clear()
        self.memory.load(previous_memory)

        # Retirer aussi le node précédent de l'historique car il sera re-traité
        self.history.pop()
        if self.memory_snapshots:
            self.memory_snapshots.pop()

        self.can_go_back = len(self.history) > 0

        # Cacher tous les composants actifs pour rafraîchir l'affichage
        self.gui.hide_all_components()

        return True

    # ==================== Sauvegarde et chargement ====================

    def save_game(self, slot: int, custom_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Sauvegarde l'état actuel du jeu.

        Args:
            slot: Numéro du slot (0 = auto-save, 1-3 = manuel)
            custom_data: Données custom à sauvegarder

        Returns:
            True si la sauvegarde a réussi
        """
        if not self.current_node:
            print("❌ Impossible de sauvegarder: aucun node actif")
            return False

        # Récupérer les images et la musique actuelles
        if custom_data is None:
            custom_data = {}

        # Sauvegarder toutes les images (layers)
        image_component = self.gui._components.get('image')
        if image_component and hasattr(image_component, 'get_layers'):
            layers = image_component.get_layers()
            if layers:
                custom_data['image_layers'] = layers

        # Sauvegarder toutes les pistes audio
        music_component = self.gui._components.get('music')
        if music_component and hasattr(music_component, 'get_tracks'):
            tracks = music_component.get_tracks()
            if tracks:
                custom_data['music_tracks'] = tracks

        return self.saver.save(
            slot=slot,
            current_node=self.current_node,
            memory_state=self.memory.get_all(),
            history=self.history.copy(),
            custom_data=custom_data
        )

    def load_game(self, slot: int) -> bool:
        """
        Charge une sauvegarde et restaure l'état du jeu.

        Args:
            slot: Numéro du slot

        Returns:
            True si le chargement a réussi
        """
        save_data = self.saver.load(slot)
        if not save_data:
            print(f"❌ Aucune sauvegarde trouvée dans le slot {slot}")
            return False

        # Restaurer l'état
        self.memory.clear()
        self.memory.load(save_data.memory_state)
        self.history = save_data.history.copy()
        self.current_node = save_data.current_node

        # Restaurer les images (layers) si elles existent
        if save_data.custom_data and 'image_layers' in save_data.custom_data:
            layers = save_data.custom_data['image_layers']
            for layer_id, image_path in layers.items():
                self.gui.show_component('image', image_path=image_path, layer=int(layer_id))

        # Restaurer les pistes audio si elles existent
        if save_data.custom_data and 'music_tracks' in save_data.custom_data:
            tracks = save_data.custom_data['music_tracks']
            for track_id, music_path in tracks.items():
                # Note: on ne sauvegarde pas le mode repeat, donc on utilise True par défaut
                self.gui.show_component('music', music_path=music_path, track=int(track_id), repeat=True)

        print(f"✓ Partie chargée (node: {self.current_node})")
        return True

    def auto_save(self, custom_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Sauvegarde automatique (slot 0).

        Args:
            custom_data: Données custom

        Returns:
            True si la sauvegarde a réussi
        """
        return self.save_game(0, custom_data)

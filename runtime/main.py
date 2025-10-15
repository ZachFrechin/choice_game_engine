"""
Runtime Main - Lance le moteur de jeu avec architecture NodeManager

Usage:
    python runtime/main.py <template.json>
    python runtime/main.py templates/jeu.json
"""

import sys
import argparse
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from runtime.core.game_engine import GameEngine
from runtime.core.manager_loader import ManagerLoader
from runtime.managers import (
    TextDisplayManager,
    ChoiceInputManager,
    VariableSetterManager,
    ConditionEvaluatorManager,
    BackgroundManager,
    MassInitManager,
    MusicManager
)
from runtime.ui.components import (
    TextDialogComponent,
    ChoiceDialogComponent,
    BackgroundImageComponent,
    GameMenuComponent,
    PauseMenuComponent,
    MusicComponent,
    CharacterPortraitComponent
)
from PyQt6.QtCore import Qt


def setup_input_events(engine: GameEngine) -> None:
    """
    Configure tous les événements clavier et souris du jeu.

    Args:
        engine: Instance du GameEngine
    """
    def open_pause_menu():
        """Ouvre le menu pause et gère les actions."""
        action = engine.gui.show_component('pause_menu')
        if action == 'save':
            success = engine.save_game(slot=1)
            if success:
                print("✓ Partie sauvegardée")
            else:
                print("❌ Erreur lors de la sauvegarde")
        elif action == 'load':
            success = engine.load_game(slot=1)
            if success:
                print("✓ Partie chargée")
            else:
                print("❌ Aucune sauvegarde trouvée")
        elif action == 'quit':
            # Retourner au menu principal
            engine.return_to_menu()

    # Enregistrer la touche ESC pour ouvrir le menu pause
    engine.key_handler.register_key(Qt.Key.Key_Escape, open_pause_menu)

    # Le scroll back est déjà configuré via le callback dans GameEngine.__init__


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='Moteur de jeu à choix')
    parser.add_argument('template', type=str, help='Chemin vers le fichier template (.json)')
    parser.add_argument('--start', type=str, help='ID du nœud de départ (optionnel)', default=None)

    args = parser.parse_args()

    # Vérifier que le fichier existe
    template_path = Path(args.template)
    if not template_path.exists():
        print(f"Erreur: Template '{template_path}' introuvable")
        sys.exit(1)

    # Créer le moteur
    engine = GameEngine()

    # Enregistrer les composants GUI de base
    print("[Runtime] Enregistrement des composants GUI...")
    engine.gui.register_component_type('text_dialog', TextDialogComponent)
    engine.gui.register_component_type('choice_dialog', ChoiceDialogComponent)
    engine.gui.register_component_type('background_image', BackgroundImageComponent)
    engine.gui.register_component_type('game_menu', GameMenuComponent)
    engine.gui.register_component_type('pause_menu', PauseMenuComponent)
    engine.gui.register_component_type('music', MusicComponent)
    engine.gui.register_component_type('character_portrait', CharacterPortraitComponent)
    print("  ✓ text_dialog")
    print("  ✓ choice_dialog")
    print("  ✓ background_image")
    print("  ✓ game_menu")
    print("  ✓ pause_menu")
    print("  ✓ music")
    print("  ✓ character_portrait")

    # Configuration des événements clavier et souris
    print("\n[Runtime] Configuration des événements...")
    setup_input_events(engine)
    print("  ✓ ESC → Menu pause")
    print("  ✓ Scroll Up → Retour en arrière")

    # Enregistrer les NodeManagers pour chaque type de node
    print("\n[Runtime] Enregistrement des managers...")

    # Manager pour les nodes de texte
    text_manager = TextDisplayManager()
    engine.register_manager('text.text', text_manager)
    print(f"  ✓ {text_manager.id} → text.text")

    # Manager pour les nodes de choix
    choice_manager = ChoiceInputManager()
    engine.register_manager('choice.choice', choice_manager)
    print(f"  ✓ {choice_manager.id} → choice.choice")

    # Manager pour les nodes de variables
    variable_manager = VariableSetterManager()
    engine.register_manager('variables.variable', variable_manager)
    print(f"  ✓ {variable_manager.id} → variables.variable")

    # Manager pour les nodes de condition
    condition_manager = ConditionEvaluatorManager()
    engine.register_manager('variables.condition', condition_manager)
    print(f"  ✓ {condition_manager.id} → variables.condition")

    # Manager pour les nodes de background
    background_manager = BackgroundManager()
    engine.register_manager('background.background', background_manager)
    print(f"  ✓ {background_manager.id} → background.background")

    # Manager pour les nodes de massinit
    massinit_manager = MassInitManager()
    engine.register_manager('massinit.massinit', massinit_manager)
    print(f"  ✓ {massinit_manager.id} → massinit.massinit")

    # Manager pour les nodes de musique
    music_manager = MusicManager()
    engine.register_manager('music.music', music_manager)
    print(f"  ✓ {music_manager.id} → music.music")

    # Charger les managers personnalisés depuis runtime/modules/managers
    print("\n[Runtime] Chargement des managers personnalisés...")
    loader = ManagerLoader('runtime.modules.managers')
    custom_managers = loader.load_managers()

    if custom_managers:
        print(f"\n[Runtime] Enregistrement des managers personnalisés...")
        count = loader.register_managers(engine)
        print(f"  → {count} association(s) enregistrée(s)")
    else:
        print("  ℹ️  Aucun manager personnalisé trouvé")

    print("\n" + "="*50)
    print("MOTEUR DE JEU - Chargement de la template")
    print("="*50)

    # Charger la template
    try:
        engine.load_template(template_path)
    except Exception as e:
        print(f"❌ Erreur lors du chargement: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Lancer le jeu
    try:
        engine.run(start_node=args.start)
    except KeyboardInterrupt:
        print("\n\n⏸️  Jeu interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

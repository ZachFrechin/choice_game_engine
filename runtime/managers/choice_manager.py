"""
ChoiceInputManager - Gère les choix interactifs
"""

from typing import Dict, Any, Optional
from ..core.interfaces.node_manager_interface import INodeManager
from ..core.memory import Memory
from ..ui.gui import GUI


class ChoiceInputManager(INodeManager):
    """
    Manager pour les nodes de choix interactifs.

    Affiche une question et des choix, demande à l'utilisateur de choisir,
    et définit 'final_next' selon le choix (ex: 'output_0', 'output_1').

    Utilise le composant ChoiceDialogComponent pour afficher les choix dans l'interface GUI.
    """

    @property
    def id(self) -> str:
        return "choice_input"

    def process(self, node: Dict[str, Any], memory: Memory, gui: Optional[GUI] = None) -> Dict[str, Any]:
        """
        Affiche les choix et récupère l'entrée utilisateur.

        Args:
            node: Node avec {'data': {'question': '...', 'choices': [...]}}
            memory: Accès aux variables
            gui: Accès au moteur GUI

        Returns:
            {'final_next': 'output_X'} où X est l'index du choix
        """
        data = node.get('data', {})
        question = data.get('question', 'Que faites-vous?')
        choices = data.get('choices', [])

        if not choices:
            print("Erreur: Aucun choix disponible")
            return {'final_next': 'output'}

        # Afficher avec le GUI si disponible
        if gui and gui.initialized:
            choice_idx = gui.show_component('choice_dialog', question=question, choices=choices)
        else:
            # Fallback: affichage console
            print("\n" + "=" * 50)
            print(question)
            print("=" * 50)

            # Afficher les choix
            for i, choice in enumerate(choices):
                choice_text = choice.get('text', f'Choix {i+1}')
                print(f"{i+1}. {choice_text}")

            # Demander le choix
            while True:
                try:
                    choice_input = input(f"\nVotre choix (1-{len(choices)}): ")
                    choice_idx = int(choice_input) - 1

                    if 0 <= choice_idx < len(choices):
                        break
                    else:
                        print(f"Veuillez entrer un nombre entre 1 et {len(choices)}")
                except ValueError:
                    print("Veuillez entrer un nombre valide")
                except KeyboardInterrupt:
                    raise

        # Retourner le port de sortie correspondant au choix
        # Ajouter ce node à l'historique car il attend une interaction utilisateur
        return {'final_next': f'output_{choice_idx}', 'add_to_history': True}

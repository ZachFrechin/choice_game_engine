"""
TextDisplayManager - Affiche le contenu des nodes de texte avec interpolation de variables
"""

import re
from typing import Dict, Any, Optional
from ..core.interfaces.node_manager_interface import INodeManager
from ..core.memory import Memory
from ..ui.gui import GUI


class TextDisplayManager(INodeManager):
    """
    Manager pour afficher le contenu des nodes de texte.

    Supporte l'interpolation de variables avec la syntaxe {{variable}}.
    Exemple: "Tu as {{score}} points" → "Tu as 42 points"

    Utilise le composant TextDialogComponent pour afficher le texte dans l'interface GUI.
    Définit 'final_next' à 'output' pour continuer.
    """

    @property
    def id(self) -> str:
        return "text_display"

    def _parse_variables(self, text: str, memory: Memory) -> str:
        """
        Parse le texte et remplace {{variable}} par les valeurs de la Memory.

        Args:
            text: Texte avec variables (ex: "Score: {{score}}")
            memory: Accès aux variables

        Returns:
            Texte avec variables remplacées

        Exemples:
            "Tu as {{score}} points" → "Tu as 42 points"
            "Nom: {{player_name}}" → "Nom: Jack"
            "{{missing}}" → "{{missing}}" (si variable n'existe pas)
        """
        # Pattern pour trouver {{variable}}
        pattern = r'\{\{([^}]+)\}\}'

        def replace_var(match):
            var_name = match.group(1).strip()
            # Récupérer la variable de la Memory
            value = memory.get(var_name)

            # Si la variable n'existe pas, garder le placeholder
            if value is None:
                return match.group(0)  # Retourne {{variable}} tel quel

            # Convertir la valeur en string
            return str(value)

        # Remplacer toutes les occurrences
        return re.sub(pattern, replace_var, text)

    def process(self, node: Dict[str, Any], memory: Memory, gui: Optional[GUI] = None) -> Dict[str, Any]:
        """
        Affiche le texte du node avec interpolation des variables.

        Args:
            node: Node avec {'data': {'content': '...', 'speaker': '...', 'character_image': '...' (optionnels)}}
            memory: Accès aux variables
            gui: Accès au moteur GUI

        Returns:
            {'final_next': 'output'}
        """
        data = node.get('data', {})
        content = data.get('content', '')
        speaker = data.get('speaker', None)
        character_image = data.get('character_image', '')

        # Parser les variables dans le contenu
        parsed_content = self._parse_variables(content, memory)

        # Parser les variables dans le speaker si présent
        if speaker:
            speaker = self._parse_variables(speaker, memory)

        # Afficher avec le GUI si disponible
        if gui and gui.initialized:
            # Afficher le portrait du personnage si spécifié
            if character_image and character_image.strip():
                gui.show_component('character_portrait', image_path=character_image)
            else:
                # Cacher le portrait s'il n'y a pas d'image
                gui.hide_component('character_portrait')

            # Afficher le texte
            gui.show_component('text_dialog', text=parsed_content, speaker=speaker)
        else:
            # Fallback: affichage console
            print("\n" + "=" * 50)
            if speaker:
                print(f"🗣️  {speaker}:")
            print(parsed_content)
            print("=" * 50)
            input("\n[Appuyez sur Entrée pour continuer]")

        # Continuer au node suivant via le port 'output'
        # Ajouter ce node à l'historique car il attend une interaction utilisateur
        return {'final_next': 'output', 'add_to_history': True}

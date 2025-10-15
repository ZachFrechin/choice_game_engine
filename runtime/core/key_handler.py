"""
KeyHandler - Gestionnaire de touches clavier pour le runtime

Permet d'enregistrer des callbacks associés à des touches et de les déclencher.
"""

from typing import Callable, Dict, Optional, Any
from PyQt6.QtCore import Qt


class KeyHandler:
    """
    Gestionnaire de touches clavier.

    Permet d'enregistrer des méthodes/callbacks pour des touches spécifiques
    et de les unregister dynamiquement.
    """

    def __init__(self):
        self._key_bindings: Dict[int, Callable] = {}

    def register_key(self, key: int, callback: Callable[[], Any]) -> None:
        """
        Enregistre un callback pour une touche.

        Args:
            key: Code Qt de la touche (ex: Qt.Key.Key_Escape)
            callback: Fonction à appeler quand la touche est pressée
        """
        self._key_bindings[key] = callback
        print(f"✓ Touche {self._key_name(key)} enregistrée")

    def unregister_key(self, key: int) -> None:
        """
        Désenregistre un callback pour une touche.

        Args:
            key: Code Qt de la touche
        """
        if key in self._key_bindings:
            del self._key_bindings[key]
            print(f"✓ Touche {self._key_name(key)} désenregistrée")

    def handle_key_press(self, key: int) -> bool:
        """
        Traite l'appui d'une touche.

        Args:
            key: Code Qt de la touche pressée

        Returns:
            True si la touche a été traitée, False sinon
        """
        if key in self._key_bindings:
            callback = self._key_bindings[key]
            callback()
            return True
        return False

    def is_registered(self, key: int) -> bool:
        """
        Vérifie si une touche est enregistrée.

        Args:
            key: Code Qt de la touche

        Returns:
            True si la touche a un callback enregistré
        """
        return key in self._key_bindings

    def clear_all(self) -> None:
        """Désenregistre toutes les touches."""
        self._key_bindings.clear()
        print("✓ Toutes les touches désenregistrées")

    def get_registered_keys(self) -> list:
        """
        Retourne la liste des touches enregistrées.

        Returns:
            Liste des codes de touches enregistrés
        """
        return list(self._key_bindings.keys())

    def _key_name(self, key: int) -> str:
        """Retourne le nom de la touche pour debug."""
        key_names = {
            Qt.Key.Key_Escape: "ESC",
            Qt.Key.Key_Space: "SPACE",
            Qt.Key.Key_Return: "RETURN",
            Qt.Key.Key_Enter: "ENTER",
            Qt.Key.Key_Tab: "TAB",
            Qt.Key.Key_Backspace: "BACKSPACE",
        }
        return key_names.get(key, f"Key_{key}")

    def __repr__(self) -> str:
        return f"KeyHandler(registered={len(self._key_bindings)})"

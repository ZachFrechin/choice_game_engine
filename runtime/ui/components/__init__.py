"""
Components - Composants GUI pour le runtime

Ce module contient les composants de base et permet l'ajout de composants custom.
"""

from .text_dialog import TextDialogComponent
from .choice_dialog import ChoiceDialogComponent
from .image import ImageComponent
from .game_menu import GameMenuComponent
from .pause_menu import PauseMenuComponent
from .music import MusicComponent
from .character_portrait import CharacterPortraitComponent

__all__ = [
    'TextDialogComponent',
    'ChoiceDialogComponent',
    'ImageComponent',
    'GameMenuComponent',
    'PauseMenuComponent',
    'MusicComponent',
    'CharacterPortraitComponent',
]

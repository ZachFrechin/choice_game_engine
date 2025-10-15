"""
UI - Interface utilisateur PyQt6 pour le runtime

Ce module contient le moteur GUI et les composants visuels.
"""

from .gui import GUI, GUIComponent, GameWindow
from .components import (
    TextDialogComponent,
    ChoiceDialogComponent,
    BackgroundImageComponent,
)

__all__ = [
    'GUI',
    'GUIComponent',
    'GameWindow',
    'TextDialogComponent',
    'ChoiceDialogComponent',
    'BackgroundImageComponent',
]

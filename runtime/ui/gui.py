"""
GUI - Moteur d'interface graphique PyQt6 pour le runtime

Gère une fenêtre de jeu et des composants visuels pouvant être utilisés par les managers.
"""

from typing import Any, Dict, Optional, List, Type
from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QEvent, QObject
from PyQt6.QtGui import QPalette, QColor
import sys


class GUIComponent(ABC):
    """
    Classe de base pour tous les composants GUI.

    Les composants peuvent être affichés, cachés, et mis à jour.
    """

    def __init__(self, gui: 'GUI'):
        self.gui = gui
        self.visible = False
        self.widget: Optional[QWidget] = None

    @abstractmethod
    def create_widget(self) -> QWidget:
        """Crée le widget Qt pour ce composant."""
        pass

    @abstractmethod
    def show(self, **kwargs) -> None:
        """Affiche le composant avec les paramètres donnés."""
        pass

    @abstractmethod
    def hide(self) -> None:
        """Cache le composant."""
        pass

    @abstractmethod
    def update(self, **kwargs) -> None:
        """Met à jour le composant."""
        pass


class KeyEventFilter(QObject):
    """Filtre d'événements pour capturer les touches clavier et molette globalement."""

    def __init__(self, key_handler, scroll_callback=None):
        super().__init__()
        self.key_handler = key_handler
        self.scroll_callback = scroll_callback

    def eventFilter(self, obj, event):
        """Filtre les événements clavier et molette."""
        if event.type() == QEvent.Type.KeyPress:
            if self.key_handler:
                handled = self.key_handler.handle_key_press(event.key())
                if handled:
                    return True  # Bloquer la propagation
        elif event.type() == QEvent.Type.Wheel:
            if self.scroll_callback:
                # Détecter scroll vers le haut (angleDelta().y() > 0)
                if event.angleDelta().y() > 0:
                    self.scroll_callback()
                    return True  # Bloquer la propagation
        return False  # Laisser passer l'événement


class GameWindow(QMainWindow):
    """
    Fenêtre principale du jeu.

    Affiche les composants GUI dans une interface de type visual novel.
    """

    def __init__(self, key_handler=None):
        super().__init__()
        self.setWindowTitle("Choice Game Engine")
        self.setMinimumSize(1024, 768)

        # Widget central (pas de layout, positionnement absolu)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.central_widget = central_widget

        # Style sombre par défaut
        self.setup_dark_theme()

        # Container pour les composants avec leurs positions
        self.component_widgets: Dict[str, QWidget] = {}

        # KeyHandler pour gérer les touches
        self.key_handler = key_handler

        # Installer un filtre d'événements global pour capturer toutes les touches
        if key_handler:
            self.event_filter = KeyEventFilter(key_handler)
            self.installEventFilter(self.event_filter)

    def setup_dark_theme(self):
        """Configure un thème neutre gris pour le jeu."""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(180, 180, 185))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.Base, QColor(240, 240, 245))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(220, 220, 225))
        palette.setColor(QPalette.ColorRole.Text, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 245))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(30, 30, 30))
        self.setPalette(palette)

    def add_component_widget(self, name: str, widget: QWidget):
        """Ajoute un widget de composant à la fenêtre avec positionnement absolu."""
        if name in self.component_widgets:
            self.remove_component_widget(name)

        self.component_widgets[name] = widget
        widget.setParent(self.central_widget)

        # Positionner et dimensionner le widget selon son type
        self._position_widget(name, widget)

        # Gérer le z-order : background en arrière-plan, portrait entre background et dialog
        if name == 'background_image':
            widget.lower()  # Mettre en arrière-plan (z=0)
        elif name == 'character_portrait':
            widget.raise_()
            # Positionner au-dessus du background mais en dessous des dialogues
            if 'background_image' in self.component_widgets:
                widget.stackUnder(self.component_widgets.get('text_dialog') or
                                 self.component_widgets.get('choice_dialog') or widget)
        else:
            widget.raise_()  # Mettre au premier plan

        widget.show()

    def _position_widget(self, name: str, widget: QWidget):
        """Positionne un widget selon son type."""
        window_width = self.central_widget.width()
        window_height = self.central_widget.height()

        if name == 'text_dialog':
            # Texte fixé en bas, toute la largeur, hauteur adaptative
            dialog_height = min(400, int(window_height * 0.45))  # 45% de la hauteur ou 400px max
            widget.setGeometry(0, window_height - dialog_height, window_width, dialog_height)
        elif name == 'choice_dialog':
            # Choix centrés
            widget.setGeometry(0, 0, window_width, window_height)
        elif name == 'background_image':
            # Image d'arrière-plan en plein écran
            widget.setGeometry(0, 0, window_width, window_height)
        elif name == 'character_portrait':
            # Portrait du personnage sur le côté droit, partiellement au-dessus de la boîte de dialogue
            portrait_width = 400  # Largeur augmentée pour éviter de couper les personnages
            portrait_height = 350
            portrait_x = window_width - portrait_width - 20  # Marge à droite
            # Position fixe en bas, légèrement au-dessus de la boîte
            portrait_y = window_height - portrait_height - 50  # 50px du bas de la fenêtre
            widget.setGeometry(portrait_x, portrait_y, portrait_width, portrait_height)
        elif name == 'game_menu' or name == 'pause_menu':
            # Menus en plein écran
            widget.setGeometry(0, 0, window_width, window_height)

    def resizeEvent(self, event):
        """Repositionne les widgets quand la fenêtre est redimensionnée."""
        super().resizeEvent(event)
        for name, widget in self.component_widgets.items():
            self._position_widget(name, widget)

    def remove_component_widget(self, name: str):
        """Retire un widget de composant de la fenêtre."""
        if name in self.component_widgets:
            widget = self.component_widgets[name]
            widget.hide()
            widget.deleteLater()
            del self.component_widgets[name]

    def clear_all_components(self):
        """Retire tous les widgets de composants."""
        for name in list(self.component_widgets.keys()):
            self.remove_component_widget(name)

    def keyPressEvent(self, event):
        """Gère les événements clavier et les transmet au KeyHandler."""
        if self.key_handler:
            handled = self.key_handler.handle_key_press(event.key())
            if handled:
                event.accept()
                return
        super().keyPressEvent(event)


class GUI:
    """
    Moteur GUI PyQt6 pour le runtime.

    Gère une fenêtre de jeu et un système de composants pouvant être utilisés
    par les NodeManagers. Similaire à Memory, c'est un outil accessible
    par tous les managers.
    """

    def __init__(self, key_handler=None, scroll_callback=None, engine=None):
        self._components: Dict[str, GUIComponent] = {}
        self._component_registry: Dict[str, Type[GUIComponent]] = {}
        self._active_components: List[str] = []
        self.initialized = False
        self.key_handler = key_handler
        self.scroll_callback = scroll_callback
        self.engine = engine  # Référence au GameEngine

        # Qt Application et fenêtre
        self.app: Optional[QApplication] = None
        self.window: Optional[GameWindow] = None

    # ==================== Gestion du cycle de vie ====================

    def initialize(self) -> None:
        """
        Initialise le GUI (création de la fenêtre Qt).

        À appeler au démarrage du moteur.
        """
        if self.initialized:
            return

        # Créer l'application Qt si elle n'existe pas
        if QApplication.instance() is None:
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()

        # Créer la fenêtre avec le KeyHandler
        self.window = GameWindow(key_handler=self.key_handler)
        self.window.show()

        # Installer le filtre d'événements sur l'application entière
        # pour capturer TOUTES les touches et le scroll, même quand un widget enfant a le focus
        if self.key_handler or self.scroll_callback:
            self.global_event_filter = KeyEventFilter(self.key_handler, self.scroll_callback)
            self.app.installEventFilter(self.global_event_filter)
            print("✓ Filtre d'événements global installé sur l'application")

        self.initialized = True
        print("✓ GUI PyQt6 initialisé")

        # Process events pour afficher la fenêtre
        self.process_events()

    def cleanup(self) -> None:
        """
        Nettoie les ressources du GUI.

        À appeler à la fin de l'exécution.
        """
        if not self.initialized:
            return

        # Cacher tous les composants actifs
        for component_name in list(self._active_components):
            self.hide_component(component_name)

        # Fermer la fenêtre
        if self.window:
            self.window.close()
            self.window = None

        self._components.clear()
        self.initialized = False
        print("✓ GUI nettoyé")

    def process_events(self):
        """Process Qt events pour garder l'interface réactive."""
        if self.app:
            self.app.processEvents()

    # ==================== Enregistrement de composants ====================

    def register_component_type(self, name: str, component_class: Type[GUIComponent]) -> None:
        """
        Enregistre un type de composant.

        Args:
            name: Nom du type de composant (ex: 'text_dialog')
            component_class: Classe du composant
        """
        self._component_registry[name] = component_class

    def create_component(self, component_type: str, instance_name: Optional[str] = None) -> GUIComponent:
        """
        Crée une instance de composant.

        Args:
            component_type: Type du composant (doit être enregistré)
            instance_name: Nom de l'instance (ou None pour utiliser le type)

        Returns:
            Instance du composant créé

        Raises:
            ValueError: Si le type n'est pas enregistré
        """
        if component_type not in self._component_registry:
            raise ValueError(
                f"Component type '{component_type}' not registered. "
                f"Available: {list(self._component_registry.keys())}"
            )

        name = instance_name or component_type
        component_class = self._component_registry[component_type]
        component = component_class(self)
        self._components[name] = component
        return component

    def get_component(self, name: str) -> Optional[GUIComponent]:
        """
        Récupère un composant par son nom.

        Args:
            name: Nom du composant

        Returns:
            Le composant ou None s'il n'existe pas
        """
        return self._components.get(name)

    def get_or_create_component(self, component_type: str, instance_name: Optional[str] = None) -> GUIComponent:
        """
        Récupère un composant existant ou le crée s'il n'existe pas.

        Args:
            component_type: Type du composant
            instance_name: Nom de l'instance

        Returns:
            Instance du composant
        """
        name = instance_name or component_type
        component = self.get_component(name)
        if component is None:
            component = self.create_component(component_type, instance_name)
        return component

    # ==================== Affichage de composants ====================

    def show_component(self, component_type: str, instance_name: Optional[str] = None, **kwargs):
        """
        Affiche un composant (le crée s'il n'existe pas).

        Args:
            component_type: Type du composant
            instance_name: Nom de l'instance
            **kwargs: Paramètres à passer au composant

        Returns:
            La valeur de retour de component.show() (peut être None, int, etc.)
        """
        component = self.get_or_create_component(component_type, instance_name)
        result = component.show(**kwargs)

        name = instance_name or component_type
        if name not in self._active_components:
            self._active_components.append(name)

        # Process events après affichage
        self.process_events()

        return result

    def hide_component(self, name: str) -> None:
        """
        Cache un composant.

        Args:
            name: Nom du composant à cacher
        """
        component = self.get_component(name)
        if component:
            component.hide()
            if name in self._active_components:
                self._active_components.remove(name)

        self.process_events()

    def update_component(self, name: str, **kwargs) -> None:
        """
        Met à jour un composant.

        Args:
            name: Nom du composant
            **kwargs: Paramètres de mise à jour
        """
        component = self.get_component(name)
        if component:
            component.update(**kwargs)
            self.process_events()

    def hide_all_components(self) -> None:
        """Cache tous les composants actifs."""
        for name in list(self._active_components):
            self.hide_component(name)

    # ==================== Helpers ====================

    def is_component_visible(self, name: str) -> bool:
        """
        Vérifie si un composant est visible.

        Args:
            name: Nom du composant

        Returns:
            True si le composant est visible
        """
        component = self.get_component(name)
        return component.visible if component else False

    def get_active_components(self) -> List[str]:
        """
        Retourne la liste des composants actifs.

        Returns:
            Liste des noms de composants actifs
        """
        return list(self._active_components)

    def __repr__(self) -> str:
        return f"GUI(components={len(self._components)}, active={len(self._active_components)})"

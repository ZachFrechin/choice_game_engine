"""
Application principale du créateur de jeux à choix
"""

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QPushButton, QFileDialog, QMessageBox,
                              QToolBar, QStatusBar, QDockWidget, QListWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from creator.core.managers.module_manager import ModuleManager
from creator.core.managers.template_manager import TemplateManager
from creator.ui.widgets.node_canvas import QtNodeCanvas
from creator.modules.base import TextModule, ChoiceModule, VariablesModule, MassInitModule
from creator.modules.base.image_module import ImageModule
from creator.modules.base.music_module import MusicModule
from creator.core.linting import LintEngine
from creator.ui.widgets.lint_panel import LintPanel

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CreatorApp(QMainWindow):
    """Application principale du créateur"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Créateur de Jeux à Choix")
        self.resize(1200, 800)

        # Managers
        self.module_manager = ModuleManager()
        self.template_manager = TemplateManager(self.module_manager)
        self.lint_engine = LintEngine()

        # Variables
        self.current_file = None

        # Charger les modules AVANT de créer l'UI
        self._load_modules()

        # Créer l'interface
        self._create_ui()

        logger.info("Application initialisée")

    def _create_ui(self):
        """Crée l'interface utilisateur"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        # Panel gauche: Bibliothèque de noeuds
        self._create_node_library_dock()
        self._update_node_library()

        # Canvas central (avec le module_manager)
        self.canvas = QtNodeCanvas(module_manager=self.module_manager)
        layout.addWidget(self.canvas, stretch=1)

        # Panel droit: Propriétés
        self._create_properties_dock()

        # Panel bas: Linting
        self._create_lint_dock()

        # Connecter la sélection de node au panel de propriétés
        self.canvas.node_selected.connect(self._on_node_selected)

        # Menu et toolbar
        self._create_menu()
        self._create_toolbar()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Prêt")

    def _create_node_library_dock(self):
        """Crée le dock de la bibliothèque de nodes"""
        dock = QDockWidget("Bibliothèque de Nodes", self)
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea |
                            Qt.DockWidgetArea.RightDockWidgetArea)

        # Liste des types de nodes
        self.node_library = QListWidget()
        dock.setWidget(self.node_library)

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

        # Connecter le double-clic pour ajouter un node
        self.node_library.itemDoubleClicked.connect(self._on_node_library_double_click)

    def _create_properties_dock(self):
        """Crée le dock des propriétés"""
        from PyQt6.QtWidgets import QScrollArea, QVBoxLayout

        dock = QDockWidget("Propriétés", self)
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea |
                            Qt.DockWidgetArea.RightDockWidgetArea)

        # Container avec scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        # Widget qui contiendra les propriétés
        self.properties_widget = QWidget()
        self.properties_layout = QVBoxLayout()
        self.properties_widget.setLayout(self.properties_layout)

        scroll.setWidget(self.properties_widget)
        dock.setWidget(scroll)

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

    def _create_lint_dock(self):
        """Crée le dock du linter"""
        dock = QDockWidget("Linting", self)
        dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea |
                            Qt.DockWidgetArea.TopDockWidgetArea)

        # Panel de linting
        self.lint_panel = LintPanel()
        dock.setWidget(self.lint_panel)

        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)

        # Connecter le bouton refresh pour lancer le linting
        self.lint_panel.refresh_button.clicked.connect(self._run_linting)

        # Connecter le clic sur un issue pour sélectionner le node
        self.lint_panel.issue_clicked.connect(self._on_lint_issue_clicked)

    def _run_linting(self):
        """Lance le linting sur le graphe actuel"""
        # Sérialiser le graphe
        graph_data = self.canvas.serialize()

        # Lancer le linting
        issues = self.lint_engine.lint_graph(graph_data)

        # Afficher les résultats
        self.lint_panel.set_issues(issues)

        # Message dans la status bar
        error_count = sum(1 for i in issues if i.severity.value == 'error')
        if error_count > 0:
            self.status_bar.showMessage(f"Linting terminé: {error_count} erreur(s) trouvée(s)")
        else:
            self.status_bar.showMessage("Linting terminé: Aucune erreur")

    def _on_lint_issue_clicked(self, node_id: str):
        """Sélectionne le node correspondant à un problème de linting"""
        # Sélectionner le node dans le canvas
        if node_id in self.canvas.nodes:
            node_item = self.canvas.node_items.get(node_id)
            if node_item:
                # Déselectionner tous les items
                for item in self.canvas.scene.selectedItems():
                    item.setSelected(False)

                # Sélectionner l'item
                node_item.setSelected(True)
                self.canvas.node_selected.emit(node_id)

                # Centrer la vue sur le node
                self.canvas.centerOn(node_item)

    def _on_node_library_double_click(self, item):
        """Ajoute un node au canvas quand on double-clique dans la bibliothèque"""
        # Récupérer le type_id stocké dans l'item
        node_type = item.data(1)

        print(f"[Main] Double-click on {node_type}")

        # Ajouter le node au centre du canvas
        center_x = self.canvas.viewport().width() / 2
        center_y = self.canvas.viewport().height() / 2

        # Convertir en coordonnées de scène
        scene_pos = self.canvas.mapToScene(int(center_x), int(center_y))

        # Récupérer les données par défaut depuis le node type
        all_types = self.module_manager.get_all_node_types()
        node_type_obj = all_types.get(node_type)

        if node_type_obj:
            default_data = node_type_obj.default_data
            print(f"[Main] Adding node: type={node_type}, pos=({scene_pos.x()}, {scene_pos.y()}), data={default_data}")
            self.canvas.add_node(node_type, scene_pos.x(), scene_pos.y(), default_data)
            self.status_bar.showMessage(f"Node '{node_type_obj.display_name}' ajouté")

    def _on_node_selected(self, node_id: str):
        """Affiche les propriétés du node sélectionné"""
        print(f"[Main] Node selected for properties: {node_id}")

        # Effacer TOUT le contenu (widgets ET items comme spacer)
        from PyQt6.QtWidgets import QWidget
        while self.properties_layout.count():
            item = self.properties_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Récupérer les infos du node
        node_data = self.canvas.nodes.get(node_id)
        if not node_data:
            return

        node_type = node_data['type']
        widget = self.canvas.node_widgets.get(node_id)

        print(f"[Main] Creating properties editor with data: {node_data.get('data', {})}")

        # Créer un titre
        from PyQt6.QtWidgets import QLabel
        title = QLabel(f"<b>{node_type}</b>")
        self.properties_layout.addWidget(title)

        # Utiliser le module pour créer l'éditeur de propriétés
        module = self.module_manager.get_module_for_node(node_type)
        if module and widget:
            # Créer un objet node-like pour compatibilité
            class NodeProxy:
                def __init__(self, node_data, widget):
                    self.data = node_data['data']
                    self.widget = widget

            node_proxy = NodeProxy(node_data, widget)

            # Le module crée son éditeur personnalisé
            editor = module.create_properties_editor(
                node_type,
                self.properties_widget,
                node_proxy,
                on_change_callback=None  # Les callbacks sont gérés par le widget
            )

            if editor:
                self.properties_layout.addWidget(editor)

        # Spacer pour pousser le contenu vers le haut
        from PyQt6.QtWidgets import QSpacerItem, QSizePolicy
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.properties_layout.addItem(spacer)

    def _create_menu(self):
        """Crée la barre de menu"""
        menubar = self.menuBar()

        # Menu Fichier
        file_menu = menubar.addMenu("Fichier")

        new_action = QAction("Nouveau", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_template)
        file_menu.addAction(new_action)

        open_action = QAction("Ouvrir...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_template)
        file_menu.addAction(open_action)

        save_action = QAction("Sauvegarder", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_template)
        file_menu.addAction(save_action)

        save_as_action = QAction("Sauvegarder sous...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_template_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        quit_action = QAction("Quitter", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Menu Édition
        edit_menu = menubar.addMenu("Édition")

        clear_action = QAction("Effacer tout", self)
        clear_action.triggered.connect(self.clear_canvas)
        edit_menu.addAction(clear_action)

    def _create_toolbar(self):
        """Crée la toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Boutons rapides
        new_btn = QPushButton("Nouveau")
        new_btn.clicked.connect(self.new_template)
        toolbar.addWidget(new_btn)

        open_btn = QPushButton("Ouvrir")
        open_btn.clicked.connect(self.open_template)
        toolbar.addWidget(open_btn)

        save_btn = QPushButton("Sauvegarder")
        save_btn.clicked.connect(self.save_template)
        toolbar.addWidget(save_btn)

    def _load_modules(self):
        """Charge les modules de base"""
        # Enregistrer les modules
        text_module = TextModule()
        choice_module = ChoiceModule()
        variables_module = VariablesModule()
        massinit_module = MassInitModule()
        image_module = ImageModule()
        music_module = MusicModule()

        self.module_manager.register_module(text_module)
        self.module_manager.register_module(choice_module)
        self.module_manager.register_module(variables_module)
        self.module_manager.register_module(massinit_module)
        self.module_manager.register_module(image_module)
        self.module_manager.register_module(music_module)

        # Enregistrer les modules dans le lint engine pour qu'ils puissent valider leurs nodes
        # Important: utiliser le nom complet avec préfixe (module_id.type_id)
        for node_type in text_module.get_node_types():
            full_type = f"{text_module.id}.{node_type.type_id}"
            self.lint_engine.register_module(full_type, text_module)
        for node_type in choice_module.get_node_types():
            full_type = f"{choice_module.id}.{node_type.type_id}"
            self.lint_engine.register_module(full_type, choice_module)
        for node_type in variables_module.get_node_types():
            full_type = f"{variables_module.id}.{node_type.type_id}"
            self.lint_engine.register_module(full_type, variables_module)
        for node_type in massinit_module.get_node_types():
            full_type = f"{massinit_module.id}.{node_type.type_id}"
            self.lint_engine.register_module(full_type, massinit_module)
        for node_type in image_module.get_node_types():
            full_type = f"{image_module.id}.{node_type.type_id}"
            self.lint_engine.register_module(full_type, image_module)
        for node_type in music_module.get_node_types():
            full_type = f"{music_module.id}.{node_type.type_id}"
            self.lint_engine.register_module(full_type, music_module)

        logger.info(f"Modules chargés: {len(self.module_manager.get_all_node_types())}")

    def _update_node_library(self):
        """Met à jour la liste des types de nodes disponibles"""
        self.node_library.clear()
        all_node_types = self.module_manager.get_all_node_types()
        for type_id, node_type in all_node_types.items():
            # Créer un item avec le display_name visible mais stocker le type_id
            from PyQt6.QtWidgets import QListWidgetItem
            item = QListWidgetItem(f"{node_type.icon} {node_type.display_name}")
            item.setData(1, type_id)  # Stocker le type_id dans les données
            self.node_library.addItem(item)

    def new_template(self):
        """Crée un nouveau template"""
        # Demander confirmation si des modifications non sauvegardées
        reply = QMessageBox.question(
            self,
            "Nouveau template",
            "Créer un nouveau template? Les modifications non sauvegardées seront perdues.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.canvas.clear()
            self.current_file = None
            self.setWindowTitle("Créateur de Jeux à Choix")
            self.status_bar.showMessage("Nouveau template créé")

    def open_template(self):
        """Ouvre un template existant"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir un template",
            "",
            "Fichiers JSON (*.json);;Tous les fichiers (*.*)"
        )

        if filename:
            template = self.template_manager.load_template(Path(filename))
            if template:
                self.canvas.deserialize(template)
                self.current_file = filename
                self.setWindowTitle(f"Créateur de Jeux à Choix - Qt - {Path(filename).name}")
                self.status_bar.showMessage(f"Template chargé: {filename}")
            else:
                QMessageBox.critical(self, "Erreur", "Impossible de charger le template")

    def save_template(self):
        """Sauvegarde le template actuel"""
        if self.current_file:
            canvas_data = self.canvas.serialize()
            viewport_state = self.canvas.get_viewport_state()
            self.template_manager.save_template(canvas_data, Path(self.current_file), viewport_state)
            self.status_bar.showMessage(f"Template sauvegardé: {self.current_file}")
        else:
            self.save_template_as()

    def save_template_as(self):
        """Sauvegarde le template sous un nouveau nom"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder le template",
            "",
            "Fichiers JSON (*.json)"
        )

        if filename:
            # Ajouter l'extension .json si nécessaire
            if not filename.endswith('.json'):
                filename += '.json'

            canvas_data = self.canvas.serialize()
            viewport_state = self.canvas.get_viewport_state()
            self.template_manager.save_template(canvas_data, Path(filename), viewport_state)
            self.current_file = filename
            self.setWindowTitle(f"Créateur de Jeux à Choix - Qt - {Path(filename).name}")
            self.status_bar.showMessage(f"Template sauvegardé: {filename}")

    def clear_canvas(self):
        """Efface tout le canvas"""
        reply = QMessageBox.question(
            self,
            "Effacer tout",
            "Êtes-vous sûr de vouloir tout effacer?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.canvas.clear()
            self.status_bar.showMessage("Canvas effacé")


def main():
    """Point d'entrée de l'application"""
    app = QApplication(sys.argv)
    window = CreatorApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

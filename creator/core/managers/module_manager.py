"""
Module Manager - Gère le chargement et l'enregistrement des modules
"""

import importlib
import importlib.util
import os
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import logging

from ..interfaces.module_interface import IModule, NodeType

logger = logging.getLogger(__name__)


class ModuleManager:
    """Gestionnaire central pour tous les modules"""

    def __init__(self):
        self._modules: Dict[str, IModule] = {}
        self._node_types: Dict[str, NodeType] = {}
        self._module_to_nodes: Dict[str, List[str]] = {}
        self._node_to_module: Dict[str, str] = {}
        self._module_paths: List[Path] = []

    def add_module_path(self, path: Path) -> None:
        """Ajoute un chemin de recherche pour les modules"""
        if path not in self._module_paths:
            self._module_paths.append(path)
            if str(path) not in sys.path:
                sys.path.insert(0, str(path))

    def load_module(self, module_path: Path) -> bool:
        """
        Charge un module depuis un fichier Python ou un dossier

        Args:
            module_path: Chemin vers le module (.py ou dossier avec __init__.py)

        Returns:
            True si le module a été chargé avec succès
        """
        try:
            if module_path.is_file() and module_path.suffix == '.py':
                # Charger un fichier Python unique
                spec = importlib.util.spec_from_file_location(
                    module_path.stem,
                    module_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

            elif module_path.is_dir() and (module_path / '__init__.py').exists():
                # Charger un module depuis un dossier
                spec = importlib.util.spec_from_file_location(
                    module_path.name,
                    module_path / '__init__.py'
                )
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_path.name] = module
                spec.loader.exec_module(module)

            else:
                logger.error(f"Invalid module path: {module_path}")
                return False

            # Chercher les classes qui implémentent IModule
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, IModule) and
                    attr != IModule):

                    # Instancier et enregistrer le module
                    module_instance = attr()
                    self.register_module(module_instance)
                    logger.info(f"Loaded module: {module_instance.name} v{module_instance.version}")
                    return True

            logger.warning(f"No IModule implementation found in {module_path}")
            return False

        except Exception as e:
            logger.error(f"Failed to load module {module_path}: {e}")
            return False

    def load_modules_from_directory(self, directory: Path) -> int:
        """
        Charge tous les modules depuis un répertoire

        Returns:
            Nombre de modules chargés avec succès
        """
        loaded_count = 0

        if not directory.exists():
            logger.warning(f"Module directory does not exist: {directory}")
            return 0

        # Parcourir tous les fichiers et dossiers
        for item in directory.iterdir():
            # Ignorer les fichiers exemple/template
            if item.stem.startswith('exemple'):
                continue

            if item.is_file() and item.suffix == '.py' and item.stem != '__init__':
                if self.load_module(item):
                    loaded_count += 1
            elif item.is_dir() and (item / '__init__.py').exists():
                if self.load_module(item):
                    loaded_count += 1

        return loaded_count

    def register_module(self, module: IModule) -> None:
        """Enregistre un module et ses types de noeuds"""
        if module.id in self._modules:
            logger.warning(f"Module {module.id} already registered, replacing...")
            self.unregister_module(module.id)

        # Initialiser le module
        module.initialize()

        # Enregistrer le module
        self._modules[module.id] = module
        self._module_to_nodes[module.id] = []

        # Enregistrer les types de noeuds
        for node_type in module.get_node_types():
            full_type_id = f"{module.id}.{node_type.type_id}"
            self._node_types[full_type_id] = node_type
            self._module_to_nodes[module.id].append(full_type_id)
            self._node_to_module[full_type_id] = module.id

            logger.debug(f"Registered node type: {full_type_id}")

    def unregister_module(self, module_id: str) -> None:
        """Désenregistre un module et nettoie ses ressources"""
        if module_id not in self._modules:
            return

        # Nettoyer le module
        module = self._modules[module_id]
        module.cleanup()

        # Supprimer les types de noeuds
        for node_type_id in self._module_to_nodes.get(module_id, []):
            del self._node_types[node_type_id]
            del self._node_to_module[node_type_id]

        # Supprimer le module
        del self._modules[module_id]
        del self._module_to_nodes[module_id]

    def get_module(self, module_id: str) -> Optional[IModule]:
        """Retourne un module par son ID"""
        return self._modules.get(module_id)

    def get_module_for_node(self, node_type_id: str) -> Optional[IModule]:
        """Retourne le module responsable d'un type de noeud"""
        module_id = self._node_to_module.get(node_type_id)
        if module_id:
            return self._modules.get(module_id)
        return None

    def get_all_modules(self) -> Dict[str, IModule]:
        """Retourne tous les modules enregistrés"""
        return self._modules.copy()

    def get_all_node_types(self) -> Dict[str, NodeType]:
        """Retourne tous les types de noeuds disponibles"""
        return self._node_types.copy()

    def get_node_types_by_category(self) -> Dict[str, List[NodeType]]:
        """Retourne les types de noeuds groupés par catégorie"""
        categories = {}
        for type_id, node_type in self._node_types.items():
            category = node_type.category
            if category not in categories:
                categories[category] = []
            categories[category].append(node_type)
        return categories

    def create_node_widget(self, node_type_id: str, canvas: Any, node_id: str, x: float, y: float) -> Optional[Any]:
        """Crée un widget pour un type de noeud donné"""
        module = self.get_module_for_node(node_type_id)
        if module:
            # Extraire le type_id local (sans le préfixe du module)
            local_type_id = node_type_id.split('.', 1)[1] if '.' in node_type_id else node_type_id
            return module.create_node_widget(local_type_id, canvas, node_id, x, y)
        return None

    def serialize_node(self, node_type_id: str, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sérialise les données d'un noeud"""
        module = self.get_module_for_node(node_type_id)
        if module:
            return module.serialize_node(node_data)
        return node_data

    def deserialize_node(self, node_type_id: str, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Désérialise les données d'un noeud"""
        module = self.get_module_for_node(node_type_id)
        if module:
            return module.deserialize_node(node_data)
        return node_data

    def export_module_list(self) -> List[Dict[str, str]]:
        """Exporte la liste des modules pour la sauvegarde"""
        return [
            {
                'id': module.id,
                'name': module.name,
                'version': module.version
            }
            for module in self._modules.values()
        ]
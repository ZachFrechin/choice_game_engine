"""
Manager Loader - Charge automatiquement les NodeManagers custom
"""

import importlib
import inspect
from pathlib import Path
from typing import List, Type
from .interfaces.node_manager_interface import INodeManager


class ManagerLoader:
    """
    Charge automatiquement les NodeManagers depuis un dossier.

    Cherche les classes qui :
    - Héritent de INodeManager
    - Ont une méthode statique get_supported_node_types()
    """

    def __init__(self, package_path: str):
        """
        Initialise le loader.

        Args:
            package_path: Chemin du package (ex: 'runtime.modules.managers')
        """
        self.package_path = package_path
        self.loaded_managers: List[Type[INodeManager]] = []

    def load_managers(self) -> List[Type[INodeManager]]:
        """
        Charge tous les managers du package.

        Returns:
            Liste des classes de managers chargées
        """
        self.loaded_managers = []

        # Construire le chemin vers le dossier
        # runtime.modules.managers → runtime/modules/managers
        module_parts = self.package_path.split('.')
        directory = Path(__file__).parent.parent

        for part in module_parts[1:]:  # Skip 'runtime'
            directory = directory / part

        if not directory.exists():
            print(f"  ⚠️  Dossier {directory.name}/ non trouvé")
            return self.loaded_managers

        # Charger tous les fichiers .py
        for file_path in directory.glob('*.py'):
            if file_path.name.startswith('_') or file_path.name.startswith('exemple'):
                continue

            module_name = file_path.stem
            full_module_path = f"{self.package_path}.{module_name}"

            try:
                # Importer le module
                module = importlib.import_module(full_module_path)

                # Chercher les classes INodeManager
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Vérifier que c'est un INodeManager (pas l'interface elle-même)
                    if (issubclass(obj, INodeManager) and
                        obj is not INodeManager and
                        hasattr(obj, 'get_supported_node_types')):

                        self.loaded_managers.append(obj)
                        print(f"  ✓ Manager chargé: {name} (depuis {module_name}.py)")

            except Exception as e:
                print(f"  ❌ Erreur lors du chargement de {module_name}.py: {e}")

        return self.loaded_managers

    def register_managers(self, engine) -> int:
        """
        Enregistre tous les managers chargés dans un GameEngine.

        Args:
            engine: Instance du GameEngine

        Returns:
            Nombre de managers enregistrés
        """
        count = 0

        for manager_class in self.loaded_managers:
            try:
                # Instancier le manager
                manager = manager_class()

                # Récupérer les types de nodes supportés
                if hasattr(manager_class, 'get_supported_node_types'):
                    node_types = manager_class.get_supported_node_types()

                    # Enregistrer pour chaque type
                    for node_type in node_types:
                        engine.register_manager(node_type, manager)
                        print(f"  ✓ {manager.id} → {node_type}")
                        count += 1

            except Exception as e:
                print(f"  ❌ Erreur lors de l'enregistrement de {manager_class.__name__}: {e}")

        return count

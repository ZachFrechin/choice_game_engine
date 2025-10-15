"""
Template Manager - Gère la sérialisation et désérialisation des templates de jeu
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class TemplateManager:
    """Gestionnaire de templates de jeu"""

    def __init__(self, module_manager=None):
        self.module_manager = module_manager
        self.current_template: Optional[Dict[str, Any]] = None
        self.current_file_path: Optional[Path] = None
        self.is_modified: bool = False

    def create_new_template(self, metadata: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Crée un nouveau template vide

        Args:
            metadata: Métadonnées du template (titre, auteur, etc.)

        Returns:
            Le template créé
        """
        template = {
            'version': '1.0.0',
            'metadata': metadata or {
                'title': 'Nouveau Jeu',
                'author': '',
                'description': '',
                'created_at': datetime.now().isoformat(),
                'modified_at': datetime.now().isoformat()
            },
            'nodes': {},
            'connections': [],
            'start_node': None,
            'modules': []
        }

        self.current_template = template
        self.current_file_path = None
        self.is_modified = False

        return template

    def save_template(self, canvas_data: Dict[str, Any], file_path: Path = None, viewport_state: Dict[str, Any] = None) -> bool:
        """
        Sauvegarde le template actuel

        Args:
            canvas_data: Données du canvas (noeuds et connexions)
            file_path: Chemin de sauvegarde (optionnel, utilise le chemin actuel si non fourni)
            viewport_state: État du viewport (zoom, scroll) - optionnel

        Returns:
            True si la sauvegarde a réussi
        """
        if file_path is None:
            file_path = self.current_file_path

        if file_path is None:
            logger.error("No file path specified for save")
            return False

        try:
            # Créer le template
            template = self._build_template_from_canvas(canvas_data, viewport_state)

            # Sauvegarder dans le fichier
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Créer le dossier assets s'il n'existe pas
            assets_folder = file_path.parent / "assets"
            assets_folder.mkdir(exist_ok=True)

            # Convertir les chemins absolus en chemins relatifs
            template = self._convert_paths_to_relative(template, file_path.parent)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)

            self.current_template = template
            self.current_file_path = file_path
            self.is_modified = False

            logger.info(f"Template saved to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save template: {e}")
            return False

    def load_template(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Charge un template depuis un fichier

        Args:
            file_path: Chemin du fichier à charger

        Returns:
            Le template chargé ou None si échec
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"Template file not found: {file_path}")
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                template = json.load(f)

            # Valider le template
            if not self._validate_template(template):
                logger.error(f"Invalid template format in {file_path}")
                return None

            # Vérifier les modules requis
            missing_modules = self._check_required_modules(template)
            if missing_modules:
                logger.warning(f"Missing modules: {', '.join(missing_modules)}")

            # Convertir les chemins relatifs en absolus pour le créateur
            template = self._convert_paths_to_absolute(template, file_path.parent)

            self.current_template = template
            self.current_file_path = file_path
            self.is_modified = False

            logger.info(f"Template loaded from {file_path}")
            return template

        except Exception as e:
            logger.error(f"Failed to load template: {e}")
            return None

    def export_template(self, canvas_data: Dict[str, Any], export_path: Path) -> bool:
        """
        Exporte le template pour le moteur de jeu

        Args:
            canvas_data: Données du canvas
            export_path: Chemin d'export

        Returns:
            True si l'export a réussi
        """
        try:
            template = self._build_template_from_canvas(canvas_data)

            # Optimiser le template pour le runtime
            optimized = self._optimize_for_runtime(template)

            # Sauvegarder
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(optimized, f, indent=None, ensure_ascii=False)

            logger.info(f"Template exported to {export_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export template: {e}")
            return False

    def _build_template_from_canvas(self, canvas_data: Dict[str, Any], viewport_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Construit un template depuis les données du canvas"""
        nodes_data = canvas_data.get('nodes', {})
        connections_data = canvas_data.get('connections', [])

        # Construire les noeuds avec sérialisation via les modules
        nodes = {}
        for node_id, node_info in nodes_data.items():
            node_type = node_info['type']
            node_data = {
                'id': node_id,
                'type': node_type,
                'position': {
                    'x': node_info['x'],
                    'y': node_info['y']
                },
                'data': node_info.get('data', {})
            }

            # Sérialiser via le module si disponible
            if self.module_manager:
                node_data = self.module_manager.serialize_node(node_type, node_data)

            nodes[node_id] = node_data

        # Construire les connexions
        connections = []
        for conn in connections_data:
            connections.append({
                'from_node': conn['from_node'],
                'from_port': conn.get('from_port', 'output'),
                'to_node': conn['to_node'],
                'to_port': conn.get('to_port', 'input')
            })

        # Déterminer le noeud de départ (premier noeud sans connexion entrante)
        start_node = self._find_start_node(nodes, connections)

        # Obtenir la liste des modules utilisés
        modules = []
        if self.module_manager:
            modules = self.module_manager.export_module_list()

        # Créer le template
        template = {
            'version': '1.0.0',
            'metadata': self.current_template.get('metadata', {}) if self.current_template else {},
            'nodes': nodes,
            'connections': connections,
            'start_node': start_node,
            'modules': modules
        }

        # Mettre à jour la date de modification
        template['metadata']['modified_at'] = datetime.now().isoformat()

        # Ajouter l'état du viewport si fourni
        if viewport_state:
            template['metadata']['viewport'] = viewport_state

        return template

    def _find_start_node(self, nodes: Dict[str, Any], connections: List[Dict[str, Any]]) -> Optional[str]:
        """Trouve le noeud de départ (noeud sans connexion entrante)"""
        if not nodes:
            return None

        # Trouver tous les noeuds qui ont des connexions entrantes
        nodes_with_input = {conn['to_node'] for conn in connections}

        # Trouver le premier noeud sans connexion entrante
        for node_id in nodes.keys():
            if node_id not in nodes_with_input:
                return node_id

        # Si tous les noeuds ont des entrées (boucle), retourner le premier
        return next(iter(nodes.keys()))

    def _validate_template(self, template: Dict[str, Any]) -> bool:
        """Valide la structure d'un template"""
        required_fields = ['version', 'metadata', 'nodes', 'connections']

        for field in required_fields:
            if field not in template:
                logger.error(f"Missing required field: {field}")
                return False

        # Valider les métadonnées
        if not isinstance(template['metadata'], dict):
            logger.error("Invalid metadata format")
            return False

        # Valider les noeuds
        if not isinstance(template['nodes'], dict):
            logger.error("Invalid nodes format")
            return False

        # Valider les connexions
        if not isinstance(template['connections'], list):
            logger.error("Invalid connections format")
            return False

        # Valider que les connexions référencent des noeuds existants
        node_ids = set(template['nodes'].keys())
        for conn in template['connections']:
            from_node = conn.get('from_node') or conn.get('from')  # Support ancien format
            to_node = conn.get('to_node') or conn.get('to')  # Support ancien format

            if from_node not in node_ids:
                logger.error(f"Connection references non-existent node: {from_node}")
                return False
            if to_node not in node_ids:
                logger.error(f"Connection references non-existent node: {to_node}")
                return False

        return True

    def _check_required_modules(self, template: Dict[str, Any]) -> List[str]:
        """Vérifie les modules requis par le template"""
        if not self.module_manager:
            return []

        required_modules = template.get('modules', [])
        loaded_modules = self.module_manager.get_all_modules()

        missing = []
        for module_info in required_modules:
            module_id = module_info['id']
            if module_id not in loaded_modules:
                missing.append(f"{module_id} v{module_info['version']}")

        return missing

    def _optimize_for_runtime(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Optimise le template pour l'exécution"""
        optimized = template.copy()

        # Supprimer les données de position (inutiles pour le runtime)
        for node_id, node_data in optimized['nodes'].items():
            if 'position' in node_data:
                del node_data['position']

        # Simplifier les métadonnées
        optimized['metadata'] = {
            'title': template['metadata'].get('title', ''),
            'author': template['metadata'].get('author', ''),
            'version': template['version']
        }

        return optimized

    def get_template_info(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations d'un template sans le charger complètement

        Args:
            file_path: Chemin du template

        Returns:
            Dictionnaire avec les infos du template
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                template = json.load(f)

            return {
                'title': template['metadata'].get('title', 'Sans titre'),
                'author': template['metadata'].get('author', 'Anonyme'),
                'description': template['metadata'].get('description', ''),
                'version': template.get('version', 'Unknown'),
                'node_count': len(template.get('nodes', {})),
                'modules': [m['name'] for m in template.get('modules', [])],
                'created_at': template['metadata'].get('created_at', ''),
                'modified_at': template['metadata'].get('modified_at', '')
            }

        except Exception as e:
            logger.error(f"Failed to read template info: {e}")
            return None

    def mark_modified(self):
        """Marque le template comme modifié"""
        self.is_modified = True

    def has_unsaved_changes(self) -> bool:
        """Vérifie s'il y a des changements non sauvegardés"""
        return self.is_modified

    def _convert_paths_to_relative(self, template: Dict[str, Any], project_dir: Path) -> Dict[str, Any]:
        """
        Convertit tous les chemins absolus en chemins relatifs par rapport au dossier du projet.

        Args:
            template: Le template à traiter
            project_dir: Le dossier du projet (où se trouve le fichier .json)

        Returns:
            Le template avec chemins relatifs
        """
        import copy
        template = copy.deepcopy(template)

        # Champs qui contiennent des chemins de fichiers
        path_fields = ['image_path', 'music_path', 'character_image']

        # Parcourir tous les nodes
        for node_id, node_data in template.get('nodes', {}).items():
            data = node_data.get('data', {})

            for field in path_fields:
                if field in data and data[field]:
                    abs_path = Path(data[field])
                    if abs_path.is_absolute() and abs_path.exists():
                        try:
                            # Essayer de créer un chemin relatif
                            rel_path = abs_path.relative_to(project_dir)
                            data[field] = str(rel_path)
                            logger.info(f"Converted {field}: {abs_path} -> {rel_path}")
                        except ValueError:
                            # Le fichier est en dehors du dossier du projet
                            # Suggestion: copier dans assets/
                            logger.warning(f"File {abs_path} is outside project directory. Consider moving to assets/")

        return template

    def _convert_paths_to_absolute(self, template: Dict[str, Any], project_dir: Path) -> Dict[str, Any]:
        """
        Convertit tous les chemins relatifs en chemins absolus par rapport au dossier du projet.

        Args:
            template: Le template à traiter
            project_dir: Le dossier du projet (où se trouve le fichier .json)

        Returns:
            Le template avec chemins absolus
        """
        import copy
        template = copy.deepcopy(template)

        # Champs qui contiennent des chemins de fichiers
        path_fields = ['image_path', 'music_path', 'character_image']

        # Parcourir tous les nodes
        for node_id, node_data in template.get('nodes', {}).items():
            data = node_data.get('data', {})

            for field in path_fields:
                if field in data and data[field]:
                    path = Path(data[field])
                    if not path.is_absolute():
                        # Convertir en chemin absolu
                        abs_path = (project_dir / path).resolve()
                        data[field] = str(abs_path)

        return template

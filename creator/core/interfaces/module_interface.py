"""
Module Interface - Définit la structure de base pour tous les modules

Architecture modulaire:
-----------------------
Le moteur (core) ne contient AUCUNE logique spécifique aux types de nœuds.
Tous les types de nœuds sont fournis par des modules.

Un module doit:
1. Hériter de IModule et implémenter ses méthodes abstraites
2. Fournir des widgets (INodeWidget) pour l'affichage visuel des nœuds
3. Déclarer les ports via get_input_ports() et get_output_ports()
4. Gérer ses propres données via update_data() et get_data()
5. Fournir un éditeur de propriétés via create_properties_editor()

Le core se charge uniquement:
- De créer/positionner les nœuds sur le canvas
- De gérer les connexions entre nœuds
- D'appeler les méthodes génériques des widgets (update_data, get_ports, etc.)
- De créer les ports visuels basés sur ce que déclare le widget

Exemple:
--------
# Mon module personnalisé
class MonModule(IModule):
    @property
    def id(self): return "mon_module"

    def get_node_types(self):
        return [NodeType(type_id="mon_type", display_name="Mon Type", ...)]

    def create_node_widget(self, node_type, canvas, node_id, x, y):
        return MonWidget(canvas, node_id, x, y)

    def create_properties_editor(self, node_type, parent, node, callback):
        # Créer l'interface d'édition personnalisée
        return mon_editor_widget
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import json


@dataclass
class NodeType:
    """Définit un type de noeud fourni par un module"""
    type_id: str
    display_name: str
    category: str
    icon: Optional[str] = None
    default_data: Dict[str, Any] = None
    properties_schema: Dict[str, Any] = None

    def __post_init__(self):
        if self.default_data is None:
            self.default_data = {}
        if self.properties_schema is None:
            self.properties_schema = {}


@dataclass
class NodeConnection:
    """Représente une connexion entre deux noeuds"""
    from_node: str
    from_port: str = "output"
    to_node: str = None
    to_port: str = "input"


class IModule(ABC):
    """Interface de base pour tous les modules"""

    @property
    @abstractmethod
    def id(self) -> str:
        """Identifiant unique du module"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Nom d'affichage du module"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Version du module"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description du module"""
        pass

    @abstractmethod
    def get_node_types(self) -> List[NodeType]:
        """Retourne la liste des types de noeuds fournis par ce module"""
        pass

    @abstractmethod
    def create_node_widget(self, node_type: str, canvas: Any) -> Any:
        """Crée le widget visuel pour un noeud de ce type"""
        pass

    @abstractmethod
    def serialize_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sérialise les données d'un noeud pour la sauvegarde"""
        pass

    @abstractmethod
    def deserialize_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Désérialise les données d'un noeud depuis la sauvegarde"""
        pass

    def initialize(self) -> None:
        """Initialise le module (optionnel)"""
        pass

    def cleanup(self) -> None:
        """Nettoie les ressources du module (optionnel)"""
        pass

    def get_properties_widget(self, node_type: str, parent: Any) -> Optional[Any]:
        """Retourne un widget pour éditer les propriétés du noeud (optionnel)"""
        return None

    def create_properties_editor(self, node_type: str, parent: Any, node: Any, on_change_callback: Optional[Callable] = None) -> Optional[Any]:
        """Crée un éditeur de propriétés personnalisé pour un type de noeud (optionnel)"""
        return None

    def validate_node(self, node_data: Dict[str, Any]) -> List[str]:
        """Valide les données d'un noeud, retourne une liste d'erreurs"""
        return []


class INodeWidget(ABC):
    """
    Interface pour les widgets de noeuds dans le canvas

    IMPORTANT - Architecture modulaire:
    -----------------------------------
    Le widget est RESPONSABLE de:
    1. Son affichage visuel (forme, texte, couleurs)
    2. Déclarer combien de ports il a (get_input_ports / get_output_ports)
    3. Mettre à jour son affichage quand les données changent (update_data)
    4. Gérer ses propres données (get_data)

    Le canvas (core) est RESPONSABLE de:
    1. Créer les ports visuellement basé sur get_input_ports() / get_output_ports()
    2. Appeler update_data() quand les propriétés changent
    3. Gérer les connexions entre ports
    4. Gérer le drag & drop, zoom, pan

    Exemple de ports dynamiques (choix multiples):
    ----------------------------------------------
    def get_output_ports(self):
        choices = self.data.get('choices', [])
        return [
            {'id': f'output_{i}', 'name': choice['text']}
            for i, choice in enumerate(choices)
        ]

    Quand les données changent (ajout/suppression de choix), le canvas:
    1. Appelle widget.update_data(new_data)
    2. Le widget met à jour son affichage
    3. Le canvas appelle get_output_ports() pour voir si le nombre a changé
    4. Si oui, recrée les ports visuels automatiquement
    """

    @abstractmethod
    def get_id(self) -> str:
        """Retourne l'ID unique du noeud"""
        pass

    @abstractmethod
    def get_position(self) -> tuple:
        """Retourne la position (x, y) du widget dans le canvas"""
        pass

    @abstractmethod
    def set_position(self, x: float, y: float) -> None:
        """Définit la position du widget (appelé lors du drag)"""
        pass

    @abstractmethod
    def get_input_ports(self) -> List[Dict[str, Any]]:
        """
        Déclare les ports d'entrée du noeud

        Returns:
            Liste de dict avec 'id' et 'name' pour chaque port
            Exemple: [{'id': 'input', 'name': 'Entrée'}]
        """
        pass

    @abstractmethod
    def get_output_ports(self) -> List[Dict[str, Any]]:
        """
        Déclare les ports de sortie du noeud (peut être dynamique!)

        Returns:
            Liste de dict avec 'id' et 'name' pour chaque port
            Exemple: [
                {'id': 'output_0', 'name': 'Choix 1'},
                {'id': 'output_1', 'name': 'Choix 2'}
            ]
        """
        pass

    @abstractmethod
    def update_data(self, data: Dict[str, Any]) -> None:
        """
        Met à jour les données et l'affichage du noeud

        Appelé quand les propriétés sont modifiées.
        Le widget doit mettre à jour son affichage visuel.
        Si le nombre de ports change, get_input_ports/get_output_ports
        doit refléter le nouveau nombre.
        """
        pass

    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """Retourne les données actuelles du noeud pour sauvegarde/sérialisation"""
        pass

    def get_port_count(self) -> Dict[str, int]:
        """Retourne le nombre de ports (helper method)"""
        input_ports = self.get_input_ports()
        output_ports = self.get_output_ports()
        return {
            'input': len(input_ports) if input_ports else 1,
            'output': len(output_ports) if output_ports else 1
        }
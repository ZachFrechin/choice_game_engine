"""
Saver - Système de sauvegarde et chargement de l'état du jeu

Permet de sauvegarder l'état complet d'une partie (variables, position, historique).
"""

import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime


class SaveData:
    """Représente une sauvegarde complète du jeu."""

    def __init__(
        self,
        current_node: str,
        memory_state: Dict[str, Any],
        history: List[str],
        timestamp: Optional[str] = None,
        custom_data: Optional[Dict[str, Any]] = None
    ):
        self.current_node = current_node
        self.memory_state = memory_state
        self.history = history
        self.timestamp = timestamp or datetime.now().isoformat()
        self.custom_data = custom_data or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convertit la sauvegarde en dictionnaire."""
        return {
            'current_node': self.current_node,
            'memory_state': self.memory_state,
            'history': self.history,
            'timestamp': self.timestamp,
            'custom_data': self.custom_data,
            'version': '1.0'
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SaveData':
        """Crée une sauvegarde depuis un dictionnaire."""
        return cls(
            current_node=data.get('current_node', ''),
            memory_state=data.get('memory_state', {}),
            history=data.get('history', []),
            timestamp=data.get('timestamp'),
            custom_data=data.get('custom_data', {})
        )


class Saver:
    """
    Système de sauvegarde et chargement du jeu.

    Gère les sauvegardes au format JSON avec support des données custom.
    """

    def __init__(self, save_directory: Optional[Path] = None):
        """
        Initialise le système de sauvegarde.

        Args:
            save_directory: Dossier de sauvegarde (par défaut: ./saves/)
        """
        self.save_directory = save_directory or Path('./saves')
        self.save_directory.mkdir(parents=True, exist_ok=True)

        # Slots de sauvegarde (auto-save + 3 slots manuels)
        self.max_slots = 4
        self.auto_save_slot = 0

    # ==================== Sauvegarde ====================

    def save(
        self,
        slot: int,
        current_node: str,
        memory_state: Dict[str, Any],
        history: List[str],
        custom_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Sauvegarde l'état du jeu dans un slot.

        Args:
            slot: Numéro du slot (0 = auto-save, 1-3 = manuel)
            current_node: ID du node actuel
            memory_state: État de la Memory
            history: Historique des nodes visités
            custom_data: Données custom à sauvegarder

        Returns:
            True si la sauvegarde a réussi
        """
        if not 0 <= slot < self.max_slots:
            print(f"❌ Slot invalide: {slot} (doit être entre 0 et {self.max_slots - 1})")
            return False

        try:
            # Créer les données de sauvegarde
            save_data = SaveData(
                current_node=current_node,
                memory_state=memory_state,
                history=history,
                custom_data=custom_data
            )

            # Sauvegarder dans un fichier JSON
            save_path = self._get_save_path(slot)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data.to_dict(), f, indent=2, ensure_ascii=False)

            slot_name = "Auto-save" if slot == 0 else f"Slot {slot}"
            print(f"✓ Sauvegarde réussie: {slot_name}")
            return True

        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            return False

    def auto_save(
        self,
        current_node: str,
        memory_state: Dict[str, Any],
        history: List[str],
        custom_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Sauvegarde automatique (slot 0).

        Args:
            current_node: ID du node actuel
            memory_state: État de la Memory
            history: Historique des nodes visités
            custom_data: Données custom

        Returns:
            True si la sauvegarde a réussi
        """
        return self.save(self.auto_save_slot, current_node, memory_state, history, custom_data)

    # ==================== Chargement ====================

    def load(self, slot: int) -> Optional[SaveData]:
        """
        Charge une sauvegarde depuis un slot.

        Args:
            slot: Numéro du slot

        Returns:
            SaveData ou None si le slot est vide
        """
        if not 0 <= slot < self.max_slots:
            print(f"❌ Slot invalide: {slot}")
            return None

        save_path = self._get_save_path(slot)
        if not save_path.exists():
            return None

        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            save_data = SaveData.from_dict(data)
            slot_name = "Auto-save" if slot == 0 else f"Slot {slot}"
            print(f"✓ Sauvegarde chargée: {slot_name}")
            return save_data

        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
            return None

    # ==================== Gestion des slots ====================

    def has_save(self, slot: int) -> bool:
        """
        Vérifie si un slot contient une sauvegarde.

        Args:
            slot: Numéro du slot

        Returns:
            True si le slot contient une sauvegarde
        """
        if not 0 <= slot < self.max_slots:
            return False

        return self._get_save_path(slot).exists()

    def get_save_info(self, slot: int) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations d'une sauvegarde sans la charger entièrement.

        Args:
            slot: Numéro du slot

        Returns:
            Dict avec timestamp, current_node, etc. ou None
        """
        if not self.has_save(slot):
            return None

        try:
            save_path = self._get_save_path(slot)
            with open(save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return {
                'slot': slot,
                'timestamp': data.get('timestamp'),
                'current_node': data.get('current_node'),
                'has_custom_data': bool(data.get('custom_data'))
            }

        except Exception:
            return None

    def list_saves(self) -> List[Dict[str, Any]]:
        """
        Liste toutes les sauvegardes disponibles.

        Returns:
            Liste des infos de sauvegarde
        """
        saves = []
        for slot in range(self.max_slots):
            info = self.get_save_info(slot)
            if info:
                saves.append(info)

        return saves

    def delete_save(self, slot: int) -> bool:
        """
        Supprime une sauvegarde.

        Args:
            slot: Numéro du slot

        Returns:
            True si la suppression a réussi
        """
        if not 0 <= slot < self.max_slots:
            return False

        save_path = self._get_save_path(slot)
        if not save_path.exists():
            return False

        try:
            save_path.unlink()
            print(f"✓ Sauvegarde supprimée: Slot {slot}")
            return True

        except Exception as e:
            print(f"❌ Erreur lors de la suppression: {e}")
            return False

    # ==================== Utilitaires ====================

    def _get_save_path(self, slot: int) -> Path:
        """Retourne le chemin du fichier de sauvegarde pour un slot."""
        return self.save_directory / f"save_slot_{slot}.json"

    def __repr__(self) -> str:
        saves_count = sum(1 for slot in range(self.max_slots) if self.has_save(slot))
        return f"Saver(directory={self.save_directory}, saves={saves_count}/{self.max_slots})"

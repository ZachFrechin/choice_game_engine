"""
Memory - Système de variables clé-valeur pour le runtime

Fournit un registre de variables avec des méthodes helper pour manipuler les valeurs.
"""

from typing import Any, Dict, Optional


class Memory:
    """
    Système de variables clé-valeur avec méthodes helper.

    Utilisé par les NodeManagers pour stocker et manipuler l'état du jeu.
    """

    def __init__(self):
        self._store: Dict[str, Any] = {}

    # ==================== Accès de base ====================

    def get(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur.

        Args:
            key: Clé de la variable
            default: Valeur par défaut si la clé n'existe pas

        Returns:
            Valeur stockée ou default
        """
        return self._store.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Définit une valeur.

        Args:
            key: Clé de la variable
            value: Valeur à stocker
        """
        self._store[key] = value

    def has(self, key: str) -> bool:
        """
        Vérifie si une clé existe.

        Args:
            key: Clé à vérifier

        Returns:
            True si la clé existe
        """
        return key in self._store

    def delete(self, key: str) -> None:
        """
        Supprime une variable.

        Args:
            key: Clé à supprimer
        """
        if key in self._store:
            del self._store[key]

    def clear(self) -> None:
        """Vide toutes les variables."""
        self._store.clear()

    # ==================== Opérations numériques ====================

    def add(self, key: str, value: float) -> float:
        """
        Ajoute une valeur (crée la variable à 0 si elle n'existe pas).

        Args:
            key: Clé de la variable
            value: Valeur à ajouter

        Returns:
            Nouvelle valeur
        """
        current = self.get(key, 0)
        new_value = current + value
        self.set(key, new_value)
        return new_value

    def subtract(self, key: str, value: float) -> float:
        """
        Soustrait une valeur.

        Args:
            key: Clé de la variable
            value: Valeur à soustraire

        Returns:
            Nouvelle valeur
        """
        return self.add(key, -value)

    def multiply(self, key: str, value: float) -> float:
        """
        Multiplie une valeur.

        Args:
            key: Clé de la variable
            value: Multiplicateur

        Returns:
            Nouvelle valeur
        """
        current = self.get(key, 0)
        new_value = current * value
        self.set(key, new_value)
        return new_value

    def divide(self, key: str, value: float) -> float:
        """
        Divise une valeur.

        Args:
            key: Clé de la variable
            value: Diviseur

        Returns:
            Nouvelle valeur

        Raises:
            ZeroDivisionError: Si value est 0
        """
        if value == 0:
            raise ZeroDivisionError(f"Cannot divide {key} by zero")
        current = self.get(key, 0)
        new_value = current / value
        self.set(key, new_value)
        return new_value

    def increment(self, key: str) -> float:
        """
        Incrémente de 1.

        Args:
            key: Clé de la variable

        Returns:
            Nouvelle valeur
        """
        return self.add(key, 1)

    def decrement(self, key: str) -> float:
        """
        Décrémente de 1.

        Args:
            key: Clé de la variable

        Returns:
            Nouvelle valeur
        """
        return self.add(key, -1)

    # ==================== Comparaisons ====================

    def compare(self, key: str, operator: str, value: Any) -> bool:
        """
        Compare une variable avec une valeur.

        Args:
            key: Clé de la variable
            operator: Opérateur ('==', '!=', '>', '<', '>=', '<=')
            value: Valeur à comparer

        Returns:
            Résultat de la comparaison

        Raises:
            ValueError: Si l'opérateur est invalide
        """
        current = self.get(key, 0)

        if operator == '==':
            return current == value
        elif operator == '!=':
            return current != value
        elif operator == '>':
            return current > value
        elif operator == '<':
            return current < value
        elif operator == '>=':
            return current >= value
        elif operator == '<=':
            return current <= value
        else:
            raise ValueError(f"Invalid operator: {operator}")

    # ==================== Utilitaires ====================

    def get_all(self) -> Dict[str, Any]:
        """
        Retourne toutes les variables.

        Returns:
            Dict de toutes les variables
        """
        return dict(self._store)

    def load(self, data: Dict[str, Any]) -> None:
        """
        Charge des variables depuis un dict.

        Args:
            data: Dict de variables à charger
        """
        self._store.update(data)

    def __repr__(self) -> str:
        return f"Memory({len(self._store)} variables)"

    def __str__(self) -> str:
        return str(self._store)

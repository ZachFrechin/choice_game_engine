"""
LintPanel - Panneau d'affichage des erreurs et warnings du linter.
"""

from typing import List, Optional, Callable
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ...core.linting import LintIssue, LintSeverity


class LintIssueWidget(QFrame):
    """Widget pour afficher un seul problème de linting."""

    clicked = pyqtSignal(str)  # Émet le node_id quand on clique

    def __init__(self, issue: LintIssue):
        super().__init__()
        self.issue = issue
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface du widget - affichage simple."""
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Couleur selon la sévérité
        if self.issue.severity == LintSeverity.ERROR:
            text_color = "#d32f2f"  # Rouge foncé
            icon = "ERROR"
        elif self.issue.severity == LintSeverity.WARNING:
            text_color = "#f57c00"  # Orange foncé
            icon = "WARN"
        else:  # INFO
            text_color = "#1976d2"  # Bleu foncé
            icon = "INFO"

        self.setStyleSheet(f"""
            LintIssueWidget {{
                background-color: transparent;
                padding: 4px 8px;
                margin: 2px 0px;
            }}
            LintIssueWidget:hover {{
                background-color: #f5f5f5;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(6)

        # Icône
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 10px;
                font-weight: bold;
                color: {text_color};
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(icon_label)

        # Message simple
        message_label = QLabel(self.issue.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {text_color};
                background: transparent;
                border: none;
            }}
        """)
        layout.addWidget(message_label, 1)

    def _darken_color(self, hex_color: str) -> str:
        """Assombrit légèrement une couleur hexadécimale."""
        # Convertir hex en RGB
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Réduire chaque composante de 10%
        r = max(0, int(r * 0.9))
        g = max(0, int(g * 0.9))
        b = max(0, int(b * 0.9))

        return f"#{r:02x}{g:02x}{b:02x}"

    def mousePressEvent(self, event):
        """Émet le signal clicked avec le node_id."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.issue.node_id)
        super().mousePressEvent(event)


class LintPanel(QWidget):
    """
    Panneau principal d'affichage des problèmes de linting.

    Affiche les erreurs, warnings et infos détectés par le LintEngine.
    """

    issue_clicked = pyqtSignal(str)  # Émet le node_id quand on clique sur un problème

    def __init__(self):
        super().__init__()
        self.issues: List[LintIssue] = []
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface du panneau."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-bottom: 1px solid #ddd;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 8, 10, 8)

        title_label = QLabel("Linting Results")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                background: transparent;
                border: none;
            }
        """)
        header_layout.addWidget(title_label)

        # Compteur
        self.count_label = QLabel("0 issues")
        self.count_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666;
                background: transparent;
                border: none;
            }
        """)
        header_layout.addWidget(self.count_label)

        header_layout.addStretch()

        # Bouton refresh
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        self.refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        header_layout.addWidget(self.refresh_button)

        layout.addWidget(header)

        # Zone de scroll pour les problèmes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)

        # Container pour les issue widgets
        self.issues_container = QWidget()
        self.issues_layout = QVBoxLayout(self.issues_container)
        self.issues_layout.setContentsMargins(10, 10, 10, 10)
        self.issues_layout.setSpacing(6)
        self.issues_layout.addStretch()

        scroll.setWidget(self.issues_container)
        layout.addWidget(scroll)

        # Message par défaut
        self._show_empty_state()

    def set_issues(self, issues: List[LintIssue]):
        """Met à jour les problèmes affichés."""
        self.issues = issues
        self._update_display()

    def clear(self):
        """Efface tous les problèmes."""
        self.issues = []
        self._update_display()

    def _update_display(self):
        """Recrée l'affichage des problèmes."""
        # Effacer les anciens widgets
        while self.issues_layout.count() > 1:  # Garder le stretch
            item = self.issues_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Mettre à jour le compteur
        error_count = sum(1 for i in self.issues if i.severity == LintSeverity.ERROR)
        warning_count = sum(1 for i in self.issues if i.severity == LintSeverity.WARNING)
        info_count = sum(1 for i in self.issues if i.severity == LintSeverity.INFO)

        count_parts = []
        if error_count > 0:
            count_parts.append(f"{error_count} error{'s' if error_count > 1 else ''}")
        if warning_count > 0:
            count_parts.append(f"{warning_count} warning{'s' if warning_count > 1 else ''}")
        if info_count > 0:
            count_parts.append(f"{info_count} info")

        if count_parts:
            self.count_label.setText(", ".join(count_parts))
        else:
            self.count_label.setText("No issues")

        # Si pas de problèmes, afficher message
        if not self.issues:
            self._show_empty_state()
            return

        # Trier: erreurs d'abord, puis warnings, puis infos
        sorted_issues = sorted(
            self.issues,
            key=lambda i: (i.severity.value, i.node_id)
        )

        # Créer les widgets
        for issue in sorted_issues:
            widget = LintIssueWidget(issue)
            widget.clicked.connect(self.issue_clicked.emit)
            self.issues_layout.insertWidget(self.issues_layout.count() - 1, widget)

    def _show_empty_state(self):
        """Affiche un message quand il n'y a pas de problèmes."""
        empty_label = QLabel("No issues found!\n\nYour graph looks good.")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_label.setStyleSheet("""
            QLabel {
                color: #999;
                font-size: 14px;
                padding: 40px;
            }
        """)
        self.issues_layout.insertWidget(0, empty_label)

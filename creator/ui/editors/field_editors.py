"""
Composants d'éditeur Qt réutilisables pour les propriétés des nodes.
"""

from PyQt6.QtWidgets import (QWidget, QLabel, QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
                              QComboBox, QRadioButton, QCheckBox, QButtonGroup,
                              QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QFrame)
from PyQt6.QtCore import Qt
from typing import Callable, Optional, Tuple, List, Dict, Any


def create_text_field(
    parent: QWidget,
    label: str,
    initial_value: str = "",
    on_change: Optional[Callable[[str], None]] = None
) -> Tuple[QWidget, QLineEdit]:
    """
    Crée un champ texte simple avec label.

    Args:
        parent: Widget parent
        label: Texte du label
        initial_value: Valeur initiale
        on_change: Callback appelé avec la nouvelle valeur à chaque modification

    Returns:
        (widget, line_edit) - Le widget conteneur et le line edit
    """
    widget = QWidget(parent)
    layout = QHBoxLayout()
    widget.setLayout(layout)
    layout.setContentsMargins(5, 5, 5, 5)

    label_widget = QLabel(label)
    layout.addWidget(label_widget)

    line_edit = QLineEdit()
    line_edit.setText(initial_value)
    layout.addWidget(line_edit, stretch=1)

    if on_change:
        line_edit.textChanged.connect(on_change)

    return widget, line_edit


def create_multiline_field(
    parent: QWidget,
    label: str,
    initial_value: str = "",
    height: int = 4,
    on_change: Optional[Callable[[str], None]] = None
) -> Tuple[QWidget, QTextEdit]:
    """
    Crée un champ texte multiligne avec label.

    Args:
        parent: Widget parent
        label: Texte du label
        initial_value: Valeur initiale
        height: Hauteur en nombre de lignes
        on_change: Callback appelé avec la nouvelle valeur à chaque modification

    Returns:
        (widget, text_edit) - Le widget conteneur et le text edit
    """
    widget = QWidget(parent)
    layout = QVBoxLayout()
    widget.setLayout(layout)
    layout.setContentsMargins(5, 5, 5, 5)

    label_widget = QLabel(label)
    layout.addWidget(label_widget)

    text_edit = QTextEdit()
    text_edit.setPlainText(initial_value)
    text_edit.setMinimumHeight(height * 20)  # Approximation
    layout.addWidget(text_edit)

    if on_change:
        text_edit.textChanged.connect(lambda: on_change(text_edit.toPlainText()))

    return widget, text_edit


def create_number_field(
    parent: QWidget,
    label: str,
    initial_value: float = 0,
    min_value: float = None,
    max_value: float = None,
    decimals: int = 0,
    on_change: Optional[Callable[[float], None]] = None
) -> Tuple[QWidget, QSpinBox]:
    """Crée un champ numérique"""
    widget = QWidget(parent)
    layout = QHBoxLayout()
    widget.setLayout(layout)
    layout.setContentsMargins(5, 5, 5, 5)

    label_widget = QLabel(label)
    layout.addWidget(label_widget)

    if decimals > 0:
        spin = QDoubleSpinBox()
        spin.setDecimals(decimals)
    else:
        spin = QSpinBox()

    if min_value is not None:
        spin.setMinimum(min_value)
    if max_value is not None:
        spin.setMaximum(max_value)

    spin.setValue(initial_value)
    layout.addWidget(spin, stretch=1)

    if on_change:
        spin.valueChanged.connect(on_change)

    return widget, spin


def create_dropdown_field(
    parent: QWidget,
    label: str,
    options: List[str],
    initial_value: str = "",
    on_change: Optional[Callable[[str], None]] = None
) -> Tuple[QWidget, QComboBox]:
    """Crée un menu déroulant"""
    widget = QWidget(parent)
    layout = QHBoxLayout()
    widget.setLayout(layout)
    layout.setContentsMargins(5, 5, 5, 5)

    label_widget = QLabel(label)
    layout.addWidget(label_widget)

    combo = QComboBox()
    combo.addItems(options)
    if initial_value and initial_value in options:
        combo.setCurrentText(initial_value)
    layout.addWidget(combo, stretch=1)

    if on_change:
        combo.currentTextChanged.connect(on_change)

    return widget, combo


def create_radio_buttons(
    parent: QWidget,
    label: str,
    options: List[Tuple[str, str]],  # Liste de tuples (value, label)
    initial_value: str = "",
    on_change: Optional[Callable[[str], None]] = None
) -> Tuple[QWidget, QButtonGroup]:
    """
    Crée des boutons radio

    Args:
        options: Liste de tuples (value, display_label) ou liste de strings
    """
    widget = QWidget(parent)
    layout = QVBoxLayout()
    widget.setLayout(layout)
    layout.setContentsMargins(5, 5, 5, 5)

    label_widget = QLabel(label)
    layout.addWidget(label_widget)

    button_group = QButtonGroup(widget)  # Important: définir le parent pour éviter la destruction

    if on_change:
        def _on_button_clicked(btn):
            value = btn.property("value")
            print(f"[RadioButtons] Button clicked, value: {value}")
            on_change(value)
        button_group.buttonClicked.connect(_on_button_clicked)

    for i, option in enumerate(options):
        # Support both tuple (value, label) and plain string
        if isinstance(option, tuple):
            value, display_label = option
        else:
            value = display_label = option

        radio = QRadioButton(display_label)
        radio.setProperty("value", value)  # Stocker la valeur
        button_group.addButton(radio, i)
        layout.addWidget(radio)
        if value == initial_value:
            radio.setChecked(True)
        print(f"[RadioButtons] Created button: {display_label} (value={value}, checked={value == initial_value})")

    return widget, button_group


def create_checkbox(
    parent: QWidget,
    label: str,
    initial_value: bool = False,
    on_change: Optional[Callable[[bool], None]] = None
) -> Tuple[QWidget, QCheckBox]:
    """Crée une case à cocher"""
    widget = QWidget(parent)
    layout = QHBoxLayout()
    widget.setLayout(layout)
    layout.setContentsMargins(5, 5, 5, 5)

    checkbox = QCheckBox(label)
    checkbox.setChecked(initial_value)
    layout.addWidget(checkbox)

    if on_change:
        checkbox.stateChanged.connect(lambda state: on_change(state == Qt.CheckState.Checked.value))

    return widget, checkbox


def create_dynamic_list_editor(
    parent: QWidget,
    label: str,
    items: List[Dict[str, Any]],
    item_template: Dict[str, Any],
    field_config: List[Dict[str, Any]],
    on_change: Optional[Callable[[List[Dict[str, Any]]], None]] = None
) -> QWidget:
    """Crée un éditeur de liste dynamique (simplifié pour Qt)"""
    widget = QWidget(parent)
    layout = QVBoxLayout()
    widget.setLayout(layout)
    layout.setContentsMargins(5, 5, 5, 5)

    label_widget = QLabel(f"<b>{label}</b>")
    layout.addWidget(label_widget)

    # TODO: Implémenter l'éditeur de liste dynamique complet
    info = QLabel("<i>Éditeur de liste: à implémenter</i>")
    layout.addWidget(info)

    return widget


def create_file_field(
    parent: QWidget,
    label: str,
    initial_value: str = "",
    file_filter: str = "All Files (*.*)",
    on_change: Optional[Callable[[str], None]] = None,
    show_preview: bool = False
) -> Tuple[QWidget, QLabel]:
    """
    Crée un champ de sélection de fichier avec boutons.

    Args:
        parent: Widget parent
        label: Texte du label
        initial_value: Chemin initial
        file_filter: Filtre pour le dialog (ex: "Images (*.png *.jpg)")
        on_change: Callback appelé avec le nouveau chemin
        show_preview: Si True, ajoute un label pour preview d'image

    Returns:
        (widget, path_label) - Le widget conteneur et le label affichant le chemin
    """
    from PyQt6.QtWidgets import QFileDialog
    from PyQt6.QtGui import QPixmap

    widget = QWidget(parent)
    layout = QVBoxLayout()
    widget.setLayout(layout)
    layout.setContentsMargins(5, 5, 5, 5)

    # Label
    label_widget = QLabel(label)
    layout.addWidget(label_widget)

    # Chemin actuel
    path_label = QLabel(initial_value or 'Aucun fichier')
    path_label.setWordWrap(True)
    path_label.setStyleSheet("padding: 5px; background: #2a2a2a; border-radius: 3px;")
    layout.addWidget(path_label)

    # Boutons
    button_layout = QHBoxLayout()

    select_button = QPushButton("Sélectionner...")
    clear_button = QPushButton("Effacer")

    button_layout.addWidget(select_button)
    button_layout.addWidget(clear_button)
    layout.addLayout(button_layout)

    # Preview optionnel
    preview_label = None
    if show_preview:
        preview_label = QLabel()
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_label.setMinimumHeight(200)
        preview_label.setStyleSheet("border: 1px solid #444; background: #1a1a1a;")
        layout.addWidget(preview_label)

    # Callbacks
    def update_preview(path: str):
        if preview_label and path:
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    300, 200,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                preview_label.setPixmap(scaled_pixmap)
            else:
                preview_label.setText('Erreur de chargement')
        elif preview_label:
            preview_label.clear()
            preview_label.setText('Aucune preview')

    def on_select():
        file_path, _ = QFileDialog.getOpenFileName(
            widget,
            "Sélectionner un fichier",
            "",
            file_filter
        )
        if file_path:
            path_label.setText(file_path)
            update_preview(file_path)
            if on_change:
                on_change(file_path)

    def on_clear():
        path_label.setText('Aucun fichier')
        update_preview('')
        if on_change:
            on_change('')

    select_button.clicked.connect(on_select)
    clear_button.clicked.connect(on_clear)

    # Charger preview initiale
    if show_preview and initial_value:
        update_preview(initial_value)

    return widget, path_label

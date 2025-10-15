"""
Composant d'éditeur pour les listes dynamiques (Qt version).
"""

import copy
from typing import Callable, List, Dict, Any, Optional, Tuple
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QScrollArea, QFrame)
from PyQt6.QtCore import Qt


def create_dynamic_list_editor(
    parent: QWidget,
    label: str,
    items: List[Dict[str, Any]],
    item_template: Dict[str, Any],
    field_config: List[Dict[str, str]],  # [{'key': 'text', 'label': 'Texte', 'width': 20}, ...]
    on_change: Optional[Callable[[List[Dict[str, Any]]], None]] = None,
    add_button_text: str = "+ Ajouter"
) -> QWidget:
    """
    Crée un éditeur de liste dynamique avec ajout/suppression d'items.

    Args:
        parent: Widget parent
        label: Label de la liste
        items: Liste d'items initiale
        item_template: Template pour les nouveaux items
        field_config: Configuration des champs (clé, label, largeur)
        on_change: Callback appelé avec la liste complète à chaque modification
        add_button_text: Texte du bouton d'ajout

    Returns:
        Widget conteneur

    Exemple:
        create_dynamic_list_editor(
            parent,
            label="Choix:",
            items=node.data.get('choices', []),
            item_template={'text': 'Nouveau choix', 'target': None},
            field_config=[{'key': 'text', 'label': 'Texte', 'width': 20}],
            on_change=lambda items: update_node({'choices': items})
        )
    """
    # Frame principal
    main_frame = QWidget(parent)
    main_layout = QVBoxLayout()
    main_frame.setLayout(main_layout)

    # Label
    title_label = QLabel(f"<b>{label}</b>")
    main_layout.addWidget(title_label)

    # ScrollArea pour les items
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setMinimumHeight(200)
    scroll_area.setMaximumHeight(400)

    # Container pour les items
    items_container = QWidget()
    items_layout = QVBoxLayout()
    items_container.setLayout(items_layout)
    scroll_area.setWidget(items_container)

    main_layout.addWidget(scroll_area)

    # Liste locale des items
    current_items = copy.deepcopy(items)
    item_entries = []

    def notify_change():
        """Notifie le changement avec une copie de la liste"""
        if on_change:
            on_change(copy.deepcopy(current_items))

    def rebuild_items():
        """Reconstruit la liste des items"""
        # Effacer tous les widgets existants
        while items_layout.count():
            item = items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        item_entries.clear()

        for i, item in enumerate(current_items):
            # Frame pour chaque item
            item_frame = QWidget()
            item_layout = QHBoxLayout()
            item_frame.setLayout(item_layout)
            item_layout.setContentsMargins(0, 2, 0, 2)

            # Numéro
            num_label = QLabel(f"{i+1}.")
            num_label.setMinimumWidth(30)
            item_layout.addWidget(num_label)

            # Champs configurables
            entry_widgets = {}
            for field in field_config:
                entry = QLineEdit()
                # Convertir la largeur en caractères (approximatif)
                width_px = field.get('width', 20) * 8
                entry.setMinimumWidth(width_px)
                entry.setText(str(item.get(field['key'], '')))
                entry_widgets[field['key']] = entry
                item_layout.addWidget(entry)

                # Mise à jour en temps réel
                def create_callback(idx, key, widget):
                    def on_text_changed(text):
                        current_items[idx][key] = text
                        notify_change()
                    return on_text_changed

                entry.textChanged.connect(create_callback(i, field['key'], entry))

            item_entries.append(entry_widgets)

            # Bouton supprimer
            def create_remove_callback(idx):
                def remove():
                    current_items.pop(idx)
                    rebuild_items()
                    notify_change()
                return remove

            remove_btn = QPushButton("✕")
            remove_btn.setMaximumWidth(30)
            remove_btn.clicked.connect(create_remove_callback(i))
            item_layout.addWidget(remove_btn)

            items_layout.addWidget(item_frame)

        # Spacer à la fin
        items_layout.addStretch()

    rebuild_items()

    # Bouton ajouter
    def add_item():
        new_item = copy.deepcopy(item_template)
        current_items.append(new_item)
        rebuild_items()
        notify_change()

    add_btn = QPushButton(add_button_text)
    add_btn.clicked.connect(add_item)
    main_layout.addWidget(add_btn)

    return main_frame

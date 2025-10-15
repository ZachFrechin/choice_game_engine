"""
Configuration du runtime - Paramètres visuels et de style

Ce fichier permet de personnaliser l'apparence des composants GUI.
Modifiez les valeurs selon vos préférences.
"""

# ==================== POLICE ET TEXTE ====================

# Police de caractères
FONT_FAMILY = "Courier New"  # Exemples: "Arial", "Helvetica", "Times New Roman", "Courier New"

# Tailles de police
FONT_SIZE_TEXT = 16          # Texte des dialogues
FONT_SIZE_SPEAKER = 16       # Nom du personnage qui parle
FONT_SIZE_CHOICE = 16        # Texte des choix
FONT_SIZE_MENU = 18          # Texte des menus

# Style de police
FONT_WEIGHT_TEXT = "normal"      # "normal" ou "bold"
FONT_WEIGHT_SPEAKER = "bold"     # "normal" ou "bold"
FONT_WEIGHT_CHOICE = "normal"    # "normal" ou "bold"
FONT_WEIGHT_MENU = "bold"        # "normal" ou "bold"

# ==================== COULEURS ====================

# Couleurs du texte
TEXT_COLOR = "#1a1a1a"           # Couleur du texte principal
SPEAKER_COLOR = "#333333"        # Couleur du nom du personnage
CHOICE_COLOR = "#1a1a1a"         # Couleur du texte des choix

# ==================== GLASSMORPHISM ====================

# Transparence des composants (0-255, 0=transparent, 255=opaque)
TEXT_BOX_OPACITY = 120           # Opacité de la boîte de dialogue
CHOICE_BOX_OPACITY = 120         # Opacité de la boîte de choix
MENU_BOX_OPACITY = 255           # Opacité des menus (plein par défaut)

# Couleur de fond des composants (RGB)
BOX_BACKGROUND_R = 240
BOX_BACKGROUND_G = 240
BOX_BACKGROUND_B = 245

# Bordures
BORDER_OPACITY = 100             # Opacité des bordures (0-255)
BORDER_RADIUS = 15               # Rayon des coins arrondis (en pixels)

# ==================== ESPACEMENTS ====================

# Marges et padding
TEXT_BOX_MARGIN = 30             # Marge autour de la boîte de texte (en pixels)
TEXT_BOX_PADDING = 25            # Padding intérieur de la boîte de texte
CHOICE_BOX_PADDING = 20          # Padding des boutons de choix

# ==================== ANIMATION ====================

# Vitesse d'affichage du texte
TEXT_DISPLAY_SPEED = "instant"   # "instant" ou "typewriter" (à implémenter)

# ==================== FOND D'ÉCRAN ====================

# Couleur de fond par défaut (si pas d'image)
BACKGROUND_COLOR_R = 180
BACKGROUND_COLOR_G = 180
BACKGROUND_COLOR_B = 185

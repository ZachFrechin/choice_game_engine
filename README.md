# Choice Game Engine

Un moteur de jeu narratif basé sur des graphes de nœuds, développé avec PyQt6. Créez des jeux à choix multiples avec une interface visuelle de type node-based editor.

## 🎮 Fonctionnalités

### Creator (Éditeur)
- **Éditeur de graphes visuel** - Créez vos histoires en reliant des nœuds
- **Système de nœuds** :
  - **Text** - Afficher du texte avec un personnage parlant optionnel
  - **Choice** - Proposer des choix au joueur
  - **Image** - Afficher des images avec système de layers (superposition)
  - **Music** - Jouer de la musique avec système de pistes et option repeat
  - **Variables** - Gérer des variables et conditions
  - **MassInit** - Initialiser plusieurs variables en une fois
- **Système de validation** - Linting en temps réel pour détecter les erreurs
- **Gestion d'assets** - Organisation automatique des fichiers dans un dossier `assets/`
- **Paths relatifs** - Projets portables et partageables

### Runtime (Moteur de jeu)
- **Interface graphique PyQt6** - Interface moderne et responsive
- **Système de sauvegarde** - Sauvegardes multiples avec restauration complète
- **Scroll-back** - Retour en arrière dans l'histoire
- **Menu pause** - Pause, sauvegarde, retour au menu
- **Portraits de personnages** - Affichage des personnages pendant les dialogues
- **Multi-layers** :
  - Images : plusieurs images superposées avec z-order
  - Audio : plusieurs pistes audio simultanées
- **Gestion de la musique** :
  - Mode boucle ou lecture unique
  - Pistes multiples pour musique de fond + effets sonores

## 📦 Installation

### Prérequis
- Python 3.11+
- PyQt6

### Installation rapide

```bash
# Cloner le repository
git clone https://github.com/VOTRE_USERNAME/choice_game_engine.git
cd choice_game_engine

# Créer un environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
# Sur macOS/Linux :
source venv/bin/activate
# Sur Windows :
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

## 🚀 Utilisation

### Lancer le Creator

```bash
# macOS/Linux
python creator/main.py

# Windows
python creator\main.py
```

Ou utilisez les scripts de lancement :
```bash
# macOS/Linux
./run_creator.sh

# Windows
run_creator.bat
```

### Lancer le Runtime

```bash
# macOS/Linux
python runtime/main.py templates/exemple.json

# Windows
python runtime\main.py templates\exemple.json
```

Ou double-cliquez sur l'exécutable (une boîte de dialogue s'ouvrira pour sélectionner le fichier de jeu).

## 🏗️ Structure du Projet

```
choice_game_engine/
├── creator/               # Éditeur de jeu
│   ├── core/             # Logique métier (modules, templates, linting)
│   ├── modules/          # Modules de nœuds (Text, Choice, Image, etc.)
│   └── ui/               # Interface graphique
├── runtime/              # Moteur de jeu
│   ├── core/             # GameEngine, Memory, Saver
│   ├── managers/         # Managers pour chaque type de nœud
│   └── ui/               # Composants GUI (dialogs, menus, etc.)
├── templates/            # Projets de jeu
│   ├── assets/          # Images, sons, musiques
│   └── exemple.json     # Exemple de jeu
└── requirements.txt      # Dépendances Python
```

## 🎨 Créer un Jeu

1. **Ouvrir le Creator** et créer un nouveau projet
2. **Ajouter des nœuds** depuis la bibliothèque (clic droit ou panel de gauche)
3. **Connecter les nœuds** en glissant depuis les ports de sortie vers les ports d'entrée
4. **Configurer les propriétés** de chaque nœud dans le panel de droite
5. **Sauvegarder** votre projet (File > Save)
6. **Tester** avec le Runtime

### Types de Nœuds

- **Start** - Point de départ du jeu (automatique)
- **Text** - Affiche du texte avec support Markdown et personnage optionnel
- **Choice** - Propose jusqu'à 4 choix au joueur
- **Image** - Affiche une image sur un layer spécifique
- **Music** - Joue de la musique sur une piste avec option repeat
- **Variable** - Modifie une variable
- **Condition** - Branchement conditionnel basé sur une variable
- **MassInit** - Initialise plusieurs variables à la fois

## 🔧 Compilation

### Compiler localement

```bash
# Installer PyInstaller
pip install pyinstaller

# Compiler le Creator
pyinstaller creator.spec --clean

# Compiler le Runtime
pyinstaller runtime.spec --clean

# Les exécutables seront dans dist/
```

Les exécutables seront disponibles dans la section **Releases** de GitHub (Windows, macOS, Linux).

> **Note macOS** : Les builds GitHub Actions peuvent nécessiter des étapes supplémentaires pour contourner les restrictions de sécurité macOS. Voir [README_MACOS.md](README_MACOS.md) pour plus d'informations.

## 📝 Exemples

Un jeu d'exemple est fourni dans `templates/exemple.json`. Ouvrez-le dans le Creator pour voir comment structurer votre jeu.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 🐛 Problèmes Connus

- **macOS** : Les builds GitHub Actions nécessitent `xattr -cr` pour retirer la quarantaine
- **Windows** : Première exécution peut être lente (antivirus)

## 💡 Fonctionnalités Futures

- [ ] Éditeur de dialogues amélioré
- [ ] Support vidéo
- [ ] Animations de transition
- [ ] Export web (HTML5)
- [ ] Multi-langue

## 📞 Support

Pour toute question ou problème :
- Ouvrez une [issue](https://github.com/VOTRE_USERNAME/choice_game_engine/issues)
- Consultez la [documentation](https://github.com/VOTRE_USERNAME/choice_game_engine/wiki)

---

🎮 Créé avec PyQt6 et ❤️

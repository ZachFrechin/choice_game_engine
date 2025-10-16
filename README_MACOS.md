# Installation sur macOS

## ⚠️ Problème connu avec les builds GitHub Actions

Les applications macOS compilées par GitHub Actions crashent actuellement au démarrage. C'est un problème connu avec PyInstaller + PyQt6 + macOS + applications non signées.

**La compilation locale fonctionne correctement** - voir ci-dessous.

---

## Compilation locale (Recommandé pour macOS)

La meilleure solution sur macOS est de compiler localement :

```bash
# Cloner le repository
git clone https://github.com/VOTRE_USERNAME/choice_game_engine.git
cd choice_game_engine

# Installer les dépendances
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Compiler Creator et Runtime
pyinstaller creator.spec --clean
pyinstaller runtime.spec --clean

# Les applications seront dans dist/
# - dist/ChoiceGameCreator.app
# - dist/ChoiceGameRuntime.app
```

Les applications compilées localement fonctionnent sans problème.

---

## Si vous avez téléchargé depuis GitHub Actions

Si malgré tout vous voulez essayer les builds GitHub (peuvent crasher), voici les étapes de sécurité :

### Solution 1: Retirer la quarantaine (Requis)

Après avoir décompressé l'archive, ouvrez le Terminal et exécutez:

```bash
cd /chemin/vers/ChoiceGameEngine-macOS
xattr -cr ChoiceGameCreator.app
xattr -cr ChoiceGameRuntime.app
```

### Solution 2: Autoriser dans les Préférences Système

1. Tentez de lancer l'application
2. Allez dans **Préférences Système** > **Confidentialité et sécurité**
3. Cliquez sur **Ouvrir quand même**

### Solution 3: Clic droit + Ouvrir

1. Faites un **clic droit** sur l'application
2. Sélectionnez **Ouvrir**
3. Cliquez sur **Ouvrir** dans la boîte de dialogue

---

## Pourquoi ce problème ?

PyQt6 nécessite que les applications macOS soient correctement signées avec un certificat Apple Developer (99$/an). Les applications compilées par GitHub Actions ne peuvent pas être signées automatiquement sans certificat.

La compilation locale évite ce problème car votre Mac fait confiance aux applications que vous compilez vous-même.

# Guide de Compilation - Choice Game Engine

Ce guide explique comment compiler le moteur en exécutables pour Windows, macOS et Linux.

## 📦 Méthodes de Compilation

### Méthode 1 : Compilation Locale (Un seul OS)

Compile uniquement pour ton système d'exploitation actuel.

#### Windows
```batch
build.bat
```

#### macOS / Linux
```bash
./build.sh
```

**Résultat :**
- `dist/ChoiceGameCreator/` - Creator standalone
- `dist/ChoiceGameRuntime/` - Runtime standalone

---

### Méthode 2 : GitHub Actions (Multi-OS) ⭐ Recommandé

Compile automatiquement pour Windows, macOS **ET** Linux via GitHub.

#### Configuration initiale (une seule fois)

1. **Créer un repo GitHub** (si ce n'est pas déjà fait) :
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/TON_USERNAME/choice_game_engine.git
   git push -u origin main
   ```

2. **Le workflow est déjà configuré** dans `.github/workflows/build.yml`

#### Comment déclencher une compilation

**Option A : Via un tag de version (recommandé)**

Crée un tag pour créer une release officielle :

```bash
# Créer un tag de version
git tag v1.0.0

# Pusher le tag sur GitHub
git push origin v1.0.0
```

➡️ GitHub compile automatiquement sur les 3 OS et crée une **Release** avec tous les exécutables téléchargeables !

**Option B : Manuellement**

1. Va sur GitHub → Onglet **Actions**
2. Clique sur **Build Executables**
3. Clique sur **Run workflow**
4. Sélectionne la branche et clique **Run workflow**

➡️ GitHub compile sur les 3 OS. Les fichiers sont téléchargeables dans l'onglet **Actions** → Ton workflow → **Artifacts**

---

## 📥 Télécharger les Builds

### Depuis une Release (tags)

Va sur : `https://github.com/TON_USERNAME/choice_game_engine/releases`

Tu verras :
- ✅ `ChoiceGameCreator-Windows.zip`
- ✅ `ChoiceGameCreator-macOS.zip`
- ✅ `ChoiceGameCreator-Linux.tar.gz`
- ✅ `ChoiceGameRuntime-Windows.zip`
- ✅ `ChoiceGameRuntime-macOS.zip`
- ✅ `ChoiceGameRuntime-Linux.tar.gz`

### Depuis les Artifacts (workflow manuel)

1. Va sur **Actions** → Ton workflow
2. Clique sur le build qui t'intéresse
3. Scroll en bas → Section **Artifacts**
4. Télécharge les archives

---

## 🚀 Distribuer ton Jeu

### Pour distribuer le Creator (pour les créateurs de jeux)

Partage le dossier `dist/ChoiceGameCreator/` (ou l'archive téléchargée depuis GitHub).

### Pour distribuer un jeu créé avec le moteur

1. **Package minimum :**
   ```
   MonJeu/
   ├── ChoiceGameRuntime.exe (ou .app sur macOS)
   ├── mon_jeu.json
   └── assets/
       ├── images/
       ├── music/
       └── ...
   ```

2. **3 façons de lancer le jeu :**

   **Option A : Double-clic** (le plus simple pour l'utilisateur)
   - L'utilisateur double-clique sur `ChoiceGameRuntime.exe`
   - Une fenêtre s'ouvre pour sélectionner le fichier `.json`

   **Option B : Drag & Drop**
   - L'utilisateur fait glisser `mon_jeu.json` sur `ChoiceGameRuntime.exe`

   **Option C : Créer un lanceur** (expérience la plus pro)

   **Windows** (`play.bat`) :
   ```batch
   @echo off
   ChoiceGameRuntime.exe mon_jeu.json
   ```

   **macOS/Linux** (`play.sh`) :
   ```bash
   #!/bin/bash
   ./ChoiceGameRuntime mon_jeu.json
   ```

3. **Distribuer :**
   - Compresse le dossier `MonJeu/` en ZIP
   - Partage sur itch.io, Steam, ton site web, etc.

---

## 🛠️ Dépannage

### Erreur "PyInstaller not found"

```bash
pip install -r requirements.txt
```

### Erreur sur macOS : "developer cannot be verified"

```bash
xattr -cr dist/ChoiceGameCreator.app
xattr -cr dist/ChoiceGameRuntime.app
```

### GitHub Actions : Échec de compilation

- Vérifie les logs dans l'onglet **Actions**
- Assure-toi que `requirements.txt` contient toutes les dépendances
- Vérifie que les fichiers `.spec` sont corrects

---

## 📊 Limites GitHub Actions

- **Gratuit** : 2000 minutes/mois pour comptes gratuits
- Chaque build prend ~5-10 minutes par OS
- **Conseil** : Ne compile que lors de releases importantes (tags)

---

## ✅ Checklist avant Release

- [ ] Tester le jeu localement
- [ ] Mettre à jour le numéro de version
- [ ] Créer un tag (`git tag v1.0.0`)
- [ ] Pusher le tag (`git push origin v1.0.0`)
- [ ] Attendre la fin de la compilation (~15-20 min)
- [ ] Télécharger et tester les 3 versions
- [ ] Publier la release sur GitHub

---

## 🎯 Exemple Complet

```bash
# 1. Faire tes modifications
git add .
git commit -m "Add new feature"
git push

# 2. Créer une release
git tag v1.0.0
git push origin v1.0.0

# 3. Attendre (GitHub compile automatiquement)

# 4. Télécharger depuis :
# https://github.com/TON_USERNAME/choice_game_engine/releases/tag/v1.0.0
```

C'est tout ! 🎉

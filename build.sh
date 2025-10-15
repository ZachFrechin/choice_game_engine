#!/bin/bash
# Script de compilation - Choice Game Engine
# Compile le Creator et le Runtime en executables macOS/Linux

set -e

echo "========================================"
echo "Choice Game Engine - Build Script"
echo "========================================"
echo ""

# Verifier si Python est installe
if ! command -v python3 &> /dev/null; then
    echo "[ERREUR] Python 3 n'est pas installe"
    exit 1
fi

# Activer le venv s'il existe
if [ -d "venv" ]; then
    echo "[INFO] Activation du venv..."
    source venv/bin/activate
else
    echo "[WARN] Venv non trouve, utilisation de Python global"
fi

# Installer les dependances de build
echo "[INFO] Installation de PyInstaller..."
pip install pyinstaller pillow
echo ""

# Nettoyer les anciens builds
echo "[INFO] Nettoyage des anciens builds..."
rm -rf dist build
echo "[OK] Nettoyage termine"
echo ""

# Compiler le Creator
echo "========================================"
echo "[INFO] Compilation du Creator..."
echo "========================================"
pyinstaller creator.spec --clean
if [ $? -ne 0 ]; then
    echo "[ERREUR] Echec de la compilation du Creator"
    exit 1
fi
echo "[OK] Creator compile: dist/ChoiceGameCreator/"
echo ""

# Compiler le Runtime
echo "========================================"
echo "[INFO] Compilation du Runtime..."
echo "========================================"
pyinstaller runtime.spec --clean
if [ $? -ne 0 ]; then
    echo "[ERREUR] Echec de la compilation du Runtime"
    exit 1
fi
echo "[OK] Runtime compile: dist/ChoiceGameRuntime/"
echo ""

# Resume
echo "========================================"
echo "BUILD TERMINE"
echo "========================================"
echo ""
echo "Creator : dist/ChoiceGameCreator/ChoiceGameCreator"
echo "Runtime : dist/ChoiceGameRuntime/ChoiceGameRuntime"
echo ""
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macOS App bundles:"
    echo "  dist/ChoiceGameCreator.app"
    echo "  dist/ChoiceGameRuntime.app"
    echo ""
fi
echo "Pour distribuer, copier les dossiers dist/ChoiceGameCreator"
echo "et dist/ChoiceGameRuntime"
echo "========================================"

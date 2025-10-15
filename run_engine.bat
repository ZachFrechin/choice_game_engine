@echo off
REM Script de lancement du Runtime - Choice Game Engine
REM Verifie et cree le venv si necessaire, installe les dependances et lance le moteur

echo ========================================
echo Choice Game Engine - Runtime
echo ========================================
echo.

REM Verifier si Python est installe
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    echo Veuillez installer Python 3.8+ depuis https://www.python.org/
    pause
    exit /b 1
)

REM Verifier si le venv existe
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Creation de l'environnement virtuel...
    python -m venv venv
    if errorlevel 1 (
        echo [ERREUR] Impossible de creer le venv
        pause
        exit /b 1
    )
    echo [OK] Environnement virtuel cree
)

REM Activer le venv
echo [INFO] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Verifier si les dependances sont installees
pip show PyQt6 >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installation des dependances...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERREUR] Impossible d'installer les dependances
        pause
        exit /b 1
    )
    echo [OK] Dependances installees
)

REM Verifier qu'un fichier de jeu est fourni
if "%~1"=="" (
    echo [ERREUR] Veuillez fournir un fichier de jeu en argument
    echo Usage: run_engine.bat chemin\vers\votre_jeu.json
    echo.
    echo Exemple: run_engine.bat templates\jeu.json
    pause
    exit /b 1
)

REM Verifier que le fichier existe
if not exist "%~1" (
    echo [ERREUR] Le fichier '%~1' n'existe pas
    pause
    exit /b 1
)

REM Lancer le runtime
echo.
echo [INFO] Lancement du jeu: %~1
echo ========================================
echo.
python runtime/main.py "%~1"

REM Desactiver le venv
deactivate

echo.
echo ========================================
echo Jeu ferme
echo ========================================
pause

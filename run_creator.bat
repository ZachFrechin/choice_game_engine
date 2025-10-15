@echo off
REM Script de lancement du Creator - Choice Game Engine
REM Verifie et cree le venv si necessaire, installe les dependances et lance le creator

echo ========================================
echo Choice Game Engine - Creator
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

REM Lancer le creator
echo.
echo [INFO] Lancement du Creator...
echo ========================================
echo.
python creator/main.py

REM Desactiver le venv
deactivate

echo.
echo ========================================
echo Creator ferme
echo ========================================
pause

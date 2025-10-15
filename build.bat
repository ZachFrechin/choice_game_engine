@echo off
REM Script de compilation - Choice Game Engine
REM Compile le Creator et le Runtime en executables Windows

echo ========================================
echo Choice Game Engine - Build Script
echo ========================================
echo.

REM Verifier si Python est installe
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe
    pause
    exit /b 1
)

REM Activer le venv s'il existe
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activation du venv...
    call venv\Scripts\activate.bat
) else (
    echo [WARN] Venv non trouve, utilisation de Python global
)

REM Installer les dependances de build
echo [INFO] Installation de PyInstaller...
pip install pyinstaller pillow
echo.

REM Nettoyer les anciens builds
echo [INFO] Nettoyage des anciens builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
echo [OK] Nettoyage termine
echo.

REM Compiler le Creator
echo ========================================
echo [INFO] Compilation du Creator...
echo ========================================
pyinstaller creator.spec --clean
if errorlevel 1 (
    echo [ERREUR] Echec de la compilation du Creator
    pause
    exit /b 1
)
echo [OK] Creator compile: dist\ChoiceGameCreator\
echo.

REM Compiler le Runtime
echo ========================================
echo [INFO] Compilation du Runtime...
echo ========================================
pyinstaller runtime.spec --clean
if errorlevel 1 (
    echo [ERREUR] Echec de la compilation du Runtime
    pause
    exit /b 1
)
echo [OK] Runtime compile: dist\ChoiceGameRuntime\
echo.

REM Resume
echo ========================================
echo BUILD TERMINE
echo ========================================
echo.
echo Creator : dist\ChoiceGameCreator\ChoiceGameCreator.exe
echo Runtime : dist\ChoiceGameRuntime\ChoiceGameRuntime.exe
echo.
echo Pour distribuer, copier les dossiers dist\ChoiceGameCreator
echo et dist\ChoiceGameRuntime
echo ========================================

pause

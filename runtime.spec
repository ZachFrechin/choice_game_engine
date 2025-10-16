# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Choice Game Engine - Runtime

Build command:
    pyinstaller runtime.spec
"""

block_cipher = None

a = Analysis(
    ['runtime/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('logo.png', '.'),  # Include logo
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtMultimedia',
        'PyQt6.sip',
    ],
    hookspath=[],
    hooksconfig={
        'PyQt6': {
            'QtLibrariesList': ['QtCore', 'QtGui', 'QtWidgets', 'QtMultimedia', 'QtDBus'],
        },
    },
    runtime_hooks=['runtime_macos_hook.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ChoiceGameRuntime',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI application, no console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo.png',  # Icon for the executable
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ChoiceGameRuntime',
)

# macOS app bundle
# Note: On macOS, we create a simpler bundle structure to avoid Qt path issues
import sys
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='ChoiceGameRuntime.app',
        icon='logo.png',
        bundle_identifier='com.choicegame.runtime',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
            'LSEnvironment': {
                'QT_MAC_WANTS_LAYER': '1',
            },
        },
    )

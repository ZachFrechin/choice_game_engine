# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Choice Game Engine - Creator

Build command:
    pyinstaller creator.spec
"""

block_cipher = None

a = Analysis(
    ['creator/main.py'],
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
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    name='ChoiceGameCreator',
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
    name='ChoiceGameCreator',
)

# macOS app bundle
app = BUNDLE(
    coll,
    name='ChoiceGameCreator.app',
    icon='logo.png',
    bundle_identifier='com.choicegame.creator',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
    },
)

"""
Runtime hook for macOS to fix Qt plugin paths in PyInstaller
This file is executed before the main application starts
"""
import sys
import os
from pathlib import Path

def _setup_qt_paths():
    """Configure Qt plugin paths for macOS bundle"""
    if sys.platform == 'darwin' and getattr(sys, 'frozen', False):
        # We're running in a PyInstaller bundle on macOS
        bundle_dir = Path(sys._MEIPASS)

        # Set Qt plugin path
        os.environ['QT_PLUGIN_PATH'] = str(bundle_dir / 'PyQt6' / 'Qt6' / 'plugins')

        # Disable Qt's own plugin discovery to avoid conflicts
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = str(bundle_dir / 'PyQt6' / 'Qt6' / 'plugins' / 'platforms')

_setup_qt_paths()

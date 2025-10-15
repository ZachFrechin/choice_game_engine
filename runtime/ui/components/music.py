"""
Music - Composant pour la musique de fond dans les jeux à choix
"""

from typing import Optional
from pathlib import Path
from PyQt6.QtWidgets import QWidget
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl
from ..gui import GUIComponent, GUI


class MusicWidget(QWidget):
    """Widget Qt pour jouer de la musique de fond."""

    def __init__(self):
        super().__init__()
        self.setup_audio()

    def setup_audio(self):
        """Configure le lecteur audio."""
        # Créer le lecteur audio et la sortie audio
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        # Configuration par défaut
        self.audio_output.setVolume(0.5)  # Volume à 50%

        # La musique boucle à l'infini
        self.player.setLoops(QMediaPlayer.Loops.Infinite)

    def play_music(self, music_path: str):
        """
        Joue un fichier audio.

        Args:
            music_path: Chemin vers le fichier audio
        """
        if not Path(music_path).exists():
            print(f"⚠️  Fichier audio introuvable: {music_path}")
            return

        # Charger et jouer la musique
        url = QUrl.fromLocalFile(str(Path(music_path).absolute()))
        self.player.setSource(url)
        self.player.play()
        print(f"🎵 Lecture de la musique: {Path(music_path).name}")

    def stop_music(self):
        """Arrête la musique."""
        self.player.stop()

    def pause_music(self):
        """Met la musique en pause."""
        self.player.pause()

    def resume_music(self):
        """Reprend la musique."""
        self.player.play()

    def set_volume(self, volume: float):
        """
        Définit le volume de la musique.

        Args:
            volume: Volume entre 0.0 et 1.0
        """
        self.audio_output.setVolume(max(0.0, min(1.0, volume)))


class MusicComponent(GUIComponent):
    """
    Composant pour jouer de la musique de fond.

    La musique joue en boucle et continue entre les nodes.
    """

    def __init__(self, gui: GUI):
        super().__init__(gui)
        self.music_path: Optional[str] = None

    def create_widget(self) -> QWidget:
        """Crée le widget Qt pour ce composant."""
        return MusicWidget()

    def show(self, music_path: str, **kwargs) -> None:
        """
        Joue la musique de fond.

        Args:
            music_path: Chemin vers le fichier audio
            **kwargs: Paramètres supplémentaires
        """
        # Créer le widget si nécessaire
        if self.widget is None:
            self.widget = self.create_widget()

        # Si c'est la même musique, ne rien faire
        if self.music_path == music_path and self.visible:
            return

        self.music_path = music_path
        self.visible = True

        # Jouer la musique
        self.widget.play_music(music_path)

    def hide(self) -> None:
        """Arrête la musique."""
        if self.widget:
            self.widget.stop_music()

        self.visible = False
        self.music_path = None

    def update(self, music_path: Optional[str] = None, **kwargs) -> None:
        """
        Change la musique en cours.

        Args:
            music_path: Nouveau chemin de musique (ou None pour garder l'actuel)
            **kwargs: Paramètres supplémentaires
        """
        if music_path is not None and music_path != self.music_path:
            self.show(music_path)

    def pause(self) -> None:
        """Met la musique en pause."""
        if self.widget and self.visible:
            self.widget.pause_music()

    def resume(self) -> None:
        """Reprend la musique."""
        if self.widget and self.visible:
            self.widget.resume_music()

    def set_volume(self, volume: float) -> None:
        """
        Définit le volume de la musique.

        Args:
            volume: Volume entre 0.0 et 1.0
        """
        if self.widget:
            self.widget.set_volume(volume)

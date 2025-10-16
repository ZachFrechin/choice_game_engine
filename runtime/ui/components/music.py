"""
Music - Composant pour la musique avec système de pistes dans les jeux à choix
"""

from typing import Optional, Dict
from pathlib import Path
from PyQt6.QtWidgets import QWidget
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl
from ..gui import GUIComponent, GUI


class MusicWidget(QWidget):
    """Widget Qt pour jouer de la musique."""

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

        # Par défaut, pas de boucle (sera configuré selon le paramètre repeat)
        self.player.setLoops(QMediaPlayer.Loops.Once)

    def play_music(self, music_path: str, repeat: bool = True):
        """
        Joue un fichier audio.

        Args:
            music_path: Chemin vers le fichier audio
            repeat: Si True, boucle à l'infini. Sinon, joue une seule fois
        """
        if not Path(music_path).exists():
            print(f"⚠️  Fichier audio introuvable: {music_path}")
            return

        # Configurer le mode de lecture (boucle ou une fois)
        if repeat:
            self.player.setLoops(QMediaPlayer.Loops.Infinite)
        else:
            self.player.setLoops(QMediaPlayer.Loops.Once)

        # Charger et jouer la musique
        url = QUrl.fromLocalFile(str(Path(music_path).absolute()))
        self.player.setSource(url)
        self.player.play()

        repeat_mode = "en boucle" if repeat else "une fois"
        print(f"🎵 Lecture de la musique ({repeat_mode}): {Path(music_path).name}")

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
    Composant pour jouer de la musique avec système de pistes.

    Permet de jouer plusieurs sons simultanément sur différentes pistes.
    Piste 0 = musique de fond principale, autres pistes = effets sonores.
    """

    def __init__(self, gui: GUI):
        super().__init__(gui)
        # Dictionnaire des pistes : {track_id: {'widget': widget, 'music_path': path, 'repeat': bool}}
        self.tracks: Dict[int, Dict] = {}

    def create_widget(self) -> QWidget:
        """Crée le widget Qt pour ce composant."""
        return MusicWidget()

    def show(self, music_path: str, track: int = 0, repeat: bool = True, **kwargs) -> None:
        """
        Joue de la musique sur une piste spécifique.

        Args:
            music_path: Chemin vers le fichier audio
            track: Piste audio (0 = musique de fond, autres = effets sonores)
            repeat: Si True, boucle. Sinon, joue une fois
            **kwargs: Paramètres supplémentaires
        """
        # Si la piste existe déjà avec la même musique et même mode repeat, ne rien faire
        if track in self.tracks:
            if (self.tracks[track]['music_path'] == music_path and
                self.tracks[track]['repeat'] == repeat):
                return

        # Créer ou mettre à jour la piste
        if track not in self.tracks:
            widget = self.create_widget()
            self.tracks[track] = {
                'widget': widget,
                'music_path': music_path,
                'repeat': repeat
            }
        else:
            # Réutiliser le widget existant
            widget = self.tracks[track]['widget']
            self.tracks[track]['music_path'] = music_path
            self.tracks[track]['repeat'] = repeat

        # Jouer la musique avec le bon mode repeat
        widget.play_music(music_path, repeat)

        self.visible = True

    def hide(self, track: Optional[int] = None) -> None:
        """
        Arrête la musique.

        Args:
            track: Piste spécifique à arrêter, ou None pour tout arrêter
        """
        if track is not None:
            # Arrêter une piste spécifique
            if track in self.tracks:
                self.tracks[track]['widget'].stop_music()
                del self.tracks[track]
        else:
            # Arrêter toutes les pistes
            for track_data in self.tracks.values():
                track_data['widget'].stop_music()
            self.tracks.clear()

        # Marquer comme invisible si plus aucune piste
        if not self.tracks:
            self.visible = False

    def update(self, music_path: Optional[str] = None, track: int = 0, repeat: bool = True, **kwargs) -> None:
        """
        Change la musique en cours sur une piste.

        Args:
            music_path: Nouveau chemin de musique (ou None pour garder l'actuel)
            track: Piste à mettre à jour
            repeat: Mode de répétition
            **kwargs: Paramètres supplémentaires
        """
        if music_path is not None:
            self.show(music_path, track, repeat)

    def pause(self, track: Optional[int] = None) -> None:
        """
        Met la musique en pause.

        Args:
            track: Piste spécifique, ou None pour toutes les pistes
        """
        if track is not None:
            if track in self.tracks and self.visible:
                self.tracks[track]['widget'].pause_music()
        else:
            for track_data in self.tracks.values():
                track_data['widget'].pause_music()

    def resume(self, track: Optional[int] = None) -> None:
        """
        Reprend la musique.

        Args:
            track: Piste spécifique, ou None pour toutes les pistes
        """
        if track is not None:
            if track in self.tracks and self.visible:
                self.tracks[track]['widget'].resume_music()
        else:
            for track_data in self.tracks.values():
                track_data['widget'].resume_music()

    def set_volume(self, volume: float, track: Optional[int] = None) -> None:
        """
        Définit le volume de la musique.

        Args:
            volume: Volume entre 0.0 et 1.0
            track: Piste spécifique, ou None pour toutes les pistes
        """
        if track is not None:
            if track in self.tracks:
                self.tracks[track]['widget'].set_volume(volume)
        else:
            for track_data in self.tracks.values():
                track_data['widget'].set_volume(volume)

    def get_tracks(self) -> Dict[int, str]:
        """
        Retourne un dictionnaire des pistes actives.

        Returns:
            Dict[track_id, music_path]
        """
        return {track_id: data['music_path'] for track_id, data in self.tracks.items()}

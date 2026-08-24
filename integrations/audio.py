import os
import platform
import shutil
import subprocess
import time


class CatRepellentAudio:
    def __init__(self, audio_path=None, volume=2.0, cooldown_seconds=15):
        self.audio_path = audio_path or os.getenv("CAT_REPELLENT_AUDIO", "shiiiii.mp3")
        self.volume = volume
        self.cooldown_seconds = cooldown_seconds
        self._last_played_at = 0
        self._process = None
        self._missing_file_reported = False

    def _command(self):
        system = platform.system()
        if system == "Darwin" and shutil.which("afplay"):
            return ["afplay", "-v", str(self.volume), self.audio_path]

        if system == "Linux":
            if shutil.which("ffplay"):
                return [
                    "ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet",
                    "-volume", "100", self.audio_path,
                ]
            if shutil.which("mpg123"):
                return ["mpg123", "-q", self.audio_path]
            if shutil.which("mpv"):
                return ["mpv", "--no-video", "--really-quiet", "--volume=100", self.audio_path]

        if system == "Windows" and shutil.which("ffplay"):
            return [
                "ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet",
                "-volume", "100", self.audio_path,
            ]

        return None

    def play(self) -> bool:
        if time.monotonic() - self._last_played_at < self.cooldown_seconds:
            return False

        if self._process is not None and self._process.poll() is None:
            return False

        if not os.path.isfile(self.audio_path):
            if not self._missing_file_reported:
                print(f"Áudio repelente não encontrado: {self.audio_path}")
                self._missing_file_reported = True
            return False

        command = self._command()
        if command is None:
            print("Nenhum reprodutor de áudio compatível foi encontrado.")
            print("Instale ffplay, mpg123 ou mpv para reproduzir o áudio.")
            return False

        try:
            self._process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self._last_played_at = time.monotonic()
            print(f"Áudio repelente reproduzido: {self.audio_path}")
            return True
        except OSError as error:
            print(f"Falha ao reproduzir áudio repelente: {error}")
            return False
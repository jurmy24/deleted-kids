import threading
import io
from pydub import AudioSegment


# Suppress the pygame welcome message
import os
import sys
from contextlib import contextmanager


@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


with suppress_stdout():
    import pygame


class AudioPlayer:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(AudioPlayer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            pygame.mixer.init()
            self._thread = None
            self._stop_event = threading.Event()
            self._initialized = True

    def _play_audio(self, audio_segment: AudioSegment):
        """Handles audio playback using pygame."""
        audio_data = io.BytesIO()
        audio_segment.export(audio_data, format="mp3")
        audio_data.seek(0)

        pygame.mixer.music.load(audio_data)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy() and not self._stop_event.is_set():
            pygame.time.wait(100)

    def play(self, audio_bytes: bytes):
        """Plays an AudioSegment object in a separate thread."""
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._play_audio, args=(audio_segment,))
        self._thread.start()

    def stop(self):
        """Stops the audio playback and joins the thread."""
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            pygame.mixer.music.stop()
            self._thread.join()
            self._thread = None

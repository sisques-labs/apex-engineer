"""Voice handler for STT and TTS"""

import queue
import threading
from typing import Callable, Optional

from .push_to_talk import PushToTalk


class VoiceHandler:
    """Handles speech-to-text and text-to-speech"""

    def __init__(
        self,
        stt_enabled: bool = True,
        tts_enabled: bool = False,
        push_to_talk_key: str = "SPACE",
        microphone_index: Optional[int] = None,
    ):
        """
        Initialize voice handler

        Args:
            stt_enabled: Enable speech-to-text
            tts_enabled: Enable text-to-speech
            push_to_talk_key: Key for push-to-talk
            microphone_index: Optional microphone device index
        """
        self.stt_enabled = stt_enabled
        self.tts_enabled = tts_enabled
        self.microphone_index = microphone_index

        # Audio recording
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.audio_thread: Optional[threading.Thread] = None

        # Push-to-talk
        self.ptt = PushToTalk(
            key=push_to_talk_key,
            on_press=self._start_recording,
            on_release=self._stop_recording,
        )

        # Callbacks
        self.on_transcription: Optional[Callable[[str], None]] = None

    def start(self) -> None:
        """Start voice handler"""
        self.ptt.start()

    def stop(self) -> None:
        """Stop voice handler"""
        self.ptt.stop()
        if self.is_recording:
            self._stop_recording()

    def _start_recording(self) -> None:
        """Start recording audio"""
        if not self.stt_enabled or self.is_recording:
            return

        self.is_recording = True
        # Start recording thread
        self.audio_thread = threading.Thread(target=self._record_audio, daemon=True)
        self.audio_thread.start()

    def _stop_recording(self) -> None:
        """Stop recording and process audio"""
        if not self.is_recording:
            return

        self.is_recording = False

        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1.0)

        # Process recorded audio
        if self.stt_enabled:
            self._process_audio()

    def _record_audio(self) -> None:
        """Record audio in a separate thread"""
        try:
            import pyaudio

            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000

            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=self.microphone_index,
                frames_per_buffer=CHUNK,
            )

            frames = []

            while self.is_recording:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            audio.terminate()

            # Store audio data
            self.audio_queue.put(b"".join(frames))

        except ImportError:
            print("pyaudio not installed. Install with: pip install pyaudio")
        except Exception as e:
            print(f"Error recording audio: {e}")

    def _process_audio(self) -> None:
        """Process recorded audio with STT"""
        try:
            if self.audio_queue.empty():
                return

            audio_data = self.audio_queue.get()

            # Use whisper or other STT library
            transcription = self._transcribe_audio(audio_data)

            if transcription and self.on_transcription:
                self.on_transcription(transcription)

        except Exception as e:
            print(f"Error processing audio: {e}")

    def _transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """
        Transcribe audio to text

        Args:
            audio_data: Raw audio bytes

        Returns:
            Transcribed text or None
        """
        try:
            import io
            import wave

            import numpy as np
            import whisper

            # Convert raw audio bytes to numpy array
            # PyAudio records in 16-bit PCM format
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            # Load whisper model
            model = whisper.load_model("base")
            
            # Transcribe
            result = model.transcribe(audio_array, language="en")
            return result["text"].strip()
        except ImportError:
            print("whisper not installed. Install with: pip install openai-whisper")
            return None
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return None

    def speak(self, text: str) -> None:
        """
        Convert text to speech

        Args:
            text: Text to speak
        """
        if not self.tts_enabled:
            return

        try:
            import pyttsx3

            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except ImportError:
            print("pyttsx3 not installed. Install with: pip install pyttsx3")
        except Exception as e:
            print(f"Error with TTS: {e}")


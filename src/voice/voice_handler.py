"""Voice handler for STT and TTS"""

import logging
import queue
import threading
import time
from typing import Callable, Optional

from .push_to_talk import PushToTalk

logger = logging.getLogger(__name__)


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
        
        # Whisper model (lazy loaded)
        self._whisper_model = None

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
        # Clean up whisper model
        self._whisper_model = None

    def _start_recording(self) -> None:
        """Start recording audio"""
        if not self.stt_enabled or self.is_recording:
            logger.debug("Recording skipped: STT disabled or already recording")
            return

        logger.info("Starting audio recording...")
        self.is_recording = True
        # Start recording thread
        self.audio_thread = threading.Thread(target=self._record_audio, daemon=True)
        self.audio_thread.start()
        logger.debug("Recording thread started")

    def _stop_recording(self) -> None:
        """Stop recording and process audio"""
        if not self.is_recording:
            logger.debug("Stop recording called but not currently recording")
            return

        logger.info("Stopping audio recording...")
        self.is_recording = False

        if self.audio_thread and self.audio_thread.is_alive():
            logger.debug("Waiting for recording thread to finish...")
            self.audio_thread.join(timeout=1.0)
            if self.audio_thread.is_alive():
                logger.warning("Recording thread did not finish within timeout")

        # Process recorded audio in a separate thread to avoid blocking
        if self.stt_enabled:
            logger.debug("Starting audio processing in background thread...")
            processing_thread = threading.Thread(target=self._process_audio, daemon=True)
            processing_thread.start()

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
                logger.warning("Audio queue is empty, nothing to process")
                return

            logger.debug("Getting audio data from queue...")
            audio_data = self.audio_queue.get()
            logger.debug(f"Audio data retrieved: {len(audio_data)} bytes")

            # Use whisper or other STT library
            logger.info("Starting audio transcription...")
            transcribe_start = time.time()
            transcription = self._transcribe_audio(audio_data)
            transcribe_time = time.time() - transcribe_start
            
            if transcription:
                logger.info(f"Transcription completed in {transcribe_time:.2f}s: {transcription}")
                if self.on_transcription:
                    try:
                        logger.debug("Calling transcription callback...")
                        self.on_transcription(transcription)
                    except Exception as callback_error:
                        logger.error(f"Error in transcription callback: {callback_error}", exc_info=True)
                        print(f"Error in transcription callback: {callback_error}")
                        import traceback
                        traceback.print_exc()
                else:
                    logger.warning("No transcription callback registered")
            else:
                logger.warning("Transcription returned empty result")

        except Exception as e:
            logger.error(f"Error processing audio: {e}", exc_info=True)
            print(f"Error processing audio: {e}")
            import traceback
            traceback.print_exc()

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

            # Check if audio data is empty
            if not audio_data or len(audio_data) == 0:
                logger.warning("Audio data is empty")
                return None

            logger.debug("Converting audio bytes to numpy array...")
            # Convert raw audio bytes to numpy array
            # PyAudio records in 16-bit PCM format
            # Use frombuffer and create a proper copy to avoid view issues
            audio_int16 = np.frombuffer(audio_data, dtype=np.int16)
            
            # Ensure audio array is not empty
            if len(audio_int16) == 0:
                logger.warning("Audio array is empty after conversion")
                return None

            # Check minimum audio length (at least 0.5 seconds at 16kHz)
            min_samples = 8000  # 0.5 seconds at 16kHz
            if len(audio_int16) < min_samples:
                logger.warning(f"Audio too short: {len(audio_int16)} samples (minimum: {min_samples})")
                return None

            logger.debug(f"Audio samples: {len(audio_int16)}, duration: ~{len(audio_int16)/16000:.2f}s")

            # Convert to float32 and normalize to [-1.0, 1.0]
            # Create a proper copy (not a view) to ensure compatibility
            audio_array = (audio_int16.astype(np.float32, copy=True) / 32768.0)
            
            # Ensure audio is 1D array (mono)
            if audio_array.ndim > 1:
                audio_array = audio_array.flatten()
            
            # Make sure array is contiguous and writable (required by whisper)
            # Use np.array() to ensure it's a standard numpy array, not a view or special type
            audio_array = np.array(audio_array, dtype=np.float32, copy=True)
            
            # Ensure it's contiguous in memory
            if not audio_array.flags['C_CONTIGUOUS']:
                audio_array = np.ascontiguousarray(audio_array, dtype=np.float32)

            # Load whisper model (cache it to avoid reloading)
            if self._whisper_model is None:
                logger.info("Loading Whisper model (first time, this may take a moment)...")
                load_start = time.time()
                self._whisper_model = whisper.load_model("base")
                load_time = time.time() - load_start
                logger.info(f"Whisper model loaded in {load_time:.2f}s")
            else:
                logger.debug("Using cached Whisper model")
            
            # Transcribe - pass the array directly
            # Use verbose=False to avoid processing segments that might cause issues
            logger.debug("Running Whisper transcription...")
            whisper_start = time.time()
            result = self._whisper_model.transcribe(
                audio_array, 
                language="en",
                verbose=False,
                condition_on_previous_text=False
            )
            whisper_time = time.time() - whisper_start
            logger.debug(f"Whisper transcription completed in {whisper_time:.2f}s")
            
            # Safely extract text from result
            # Only access the text field, avoid accessing segments which might cause the error
            if isinstance(result, dict) and "text" in result:
                text = result.get("text", "").strip()
                logger.debug(f"Extracted text: '{text}'")
                return text if text else None
            logger.warning("Whisper result missing 'text' field")
            return None
        except ImportError:
            logger.error("Whisper not installed")
            print("whisper not installed. Install with: pip install openai-whisper")
            return None
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}", exc_info=True)
            print(f"Error transcribing audio: {e}")
            import traceback
            traceback.print_exc()
            return None

    def speak(self, text: str, language: str = "en") -> None:
        """
        Convert text to speech using natural-sounding TTS (non-blocking)

        Args:
            text: Text to speak
            language: Language code (es, en, fr, etc.)
        """
        if not self.tts_enabled:
            return

        logger.info(f"Speaking text: {text[:50]}...")
        
        # Run TTS in a separate thread to avoid blocking
        tts_thread = threading.Thread(
            target=self._speak_in_thread,
            args=(text, language),
            daemon=True
        )
        tts_thread.start()
    
    def _speak_in_thread(self, text: str, language: str) -> None:
        """Internal method to run TTS in a thread"""
        try:
            # Try edge-tts first (more natural, local, free)
            if self._speak_edge_tts(text, language):
                return
            
            # Fallback to pyttsx3 if edge-tts fails
            logger.debug("Falling back to pyttsx3")
            self._speak_pyttsx3(text, language)
        except Exception as e:
            logger.error(f"Error in TTS thread: {e}", exc_info=True)

    def _speak_edge_tts(self, text: str, language: str) -> bool:
        """Use Microsoft Edge TTS (natural, local, free)"""
        try:
            import edge_tts
            import asyncio
            import tempfile
            import os
            import subprocess
            import platform
            
            # Map language codes to edge-tts voices (neural voices sound natural)
            voice_map = {
                "es": "es-ES-ElviraNeural",      # Natural Spanish female voice
                "en": "en-US-AriaNeural",         # Natural English female voice
                "fr": "fr-FR-DeniseNeural",       # Natural French female voice
            }
            
            voice = voice_map.get(language, voice_map["en"])
            logger.debug(f"Using Edge TTS voice: {voice}")
            
            async def generate_speech():
                communicate = edge_tts.Communicate(text, voice)
                temp_file = os.path.join(tempfile.gettempdir(), f"apex_engineer_tts_{os.getpid()}.mp3")
                await communicate.save(temp_file)
                return temp_file
            
            # Run async function
            temp_file = asyncio.run(generate_speech())
            
            # Play audio file - use playsound for cross-platform playback
            try:
                from playsound import playsound
                playsound(temp_file, block=True)
            except ImportError:
                # Fallback to system commands
                system = platform.system()
                if system == "Windows":
                    # Use PowerShell to play and wait
                    subprocess.run(
                        ["powershell", "-Command", f"(New-Object Media.SoundPlayer '{temp_file}').PlaySync()"],
                        check=False,
                        capture_output=True
                    )
                elif system == "Darwin":  # macOS
                    subprocess.run(["afplay", temp_file], check=True, capture_output=True)
                else:  # Linux
                    subprocess.run(["mpg123", "-q", temp_file], check=True, capture_output=True)
            
            # Clean up
            try:
                os.remove(temp_file)
            except:
                pass
            
            logger.debug("Edge TTS playback completed")
            return True
            
        except ImportError:
            logger.debug("edge-tts not installed, install with: pip install edge-tts")
            return False
        except Exception as e:
            logger.warning(f"Edge TTS failed: {e}")
            return False

    def _speak_pyttsx3(self, text: str, language: str) -> None:
        """Fallback to pyttsx3 with improved settings"""
        try:
            import pyttsx3

            engine = pyttsx3.init()
            
            # Configure for more natural sound
            # Set speech rate (words per minute) - slower is more natural
            rate = engine.getProperty('rate')
            engine.setProperty('rate', rate - 30)  # Slightly slower
            
            # Try to set a better voice based on language
            voices = engine.getProperty('voices')
            if voices:
                # Prefer female voices (usually sound more natural)
                for voice in voices:
                    if language == "es" and "spanish" in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
                    elif language == "en" and "english" in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
                    elif language == "fr" and "french" in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            
            # Set volume (0.0 to 1.0)
            engine.setProperty('volume', 0.9)
            
            logger.debug("Using pyttsx3 for TTS")
            engine.say(text)
            engine.runAndWait()
            
        except ImportError:
            logger.warning("pyttsx3 not installed. Install with: pip install pyttsx3")
            print("TTS not available. Install edge-tts (recommended) or pyttsx3")
        except Exception as e:
            logger.error(f"Error with pyttsx3 TTS: {e}")
            print(f"Error with TTS: {e}")


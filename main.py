"""Main entry point for ApexEngineer"""

import logging
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

from src.ai import GPT4AllClient
from src.config import ConfigManager
from src.telemetry import AssettoCorsaReader, ContextEngine
from src.voice import VoiceHandler


class ApexEngineer:
    """Main ApexEngineer application"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize ApexEngineer"""
        self.config = ConfigManager(config_path)

        # Configure logging level from config
        log_level = self.config.get("logging.level", "INFO").upper()
        logging.getLogger().setLevel(getattr(logging, log_level, logging.INFO))
        logger.info(f"Logging level set to: {log_level}")

        # Initialize components
        self.telemetry_reader = AssettoCorsaReader()
        self.context_engine = ContextEngine()
        self.ai_module = self._init_ai_module()
        self.voice_handler = self._init_voice_handler()

        # State
        self.running = False
        self.last_telemetry_update = 0
        self.update_rate = self.config.get("telemetry.update_rate", 10)

    def _init_ai_module(self):
        """Initialize GPT4All AI module"""
        return GPT4AllClient(
            model_name=self.config.get("ai.model_name", "mistral-7b-instruct-v0.1.Q4_0.gguf"),
            model_path=self.config.get("ai.model_path"),
            temperature=self.config.get("ai.temperature", 0.7),
            max_tokens=self.config.get("ai.max_tokens", 150),
            n_threads=self.config.get("ai.n_threads", 4),
            language=self.config.get("ai.language", "es"),
        )

    def _init_voice_handler(self):
        """Initialize voice handler"""
        return VoiceHandler(
            stt_enabled=self.config.get("voice.stt_enabled", True),
            tts_enabled=self.config.get("voice.tts_enabled", False),
            push_to_talk_key=self.config.get("voice.push_to_talk_key", "SPACE"),
            microphone_index=self.config.get("voice.microphone_index"),
        )

    def start(self) -> None:
        """Start ApexEngineer"""
        logger.info("Starting ApexEngineer...")
        print("Starting ApexEngineer...")

        # Connect to telemetry
        logger.debug("Connecting to telemetry...")
        if not self.telemetry_reader.connect():
            logger.warning("Could not connect to Assetto Corsa telemetry")
            print("Warning: Could not connect to Assetto Corsa telemetry")
            print("Running in mock mode for development")
        else:
            logger.info("Telemetry connected successfully")

        # Check AI availability
        logger.debug("Checking AI module availability...")
        if not self.ai_module.is_available():
            logger.error("GPT4All model is not available")
            print("Warning: GPT4All model is not available")
            print("Check the error messages above for details.")
            print("Make sure GPT4All is installed: pip install gpt4all")
            print("The model should download automatically on first run.")
        else:
            logger.info("AI module is ready")

        # Setup voice handler
        logger.debug("Setting up voice handler...")
        self.voice_handler.on_transcription = self._handle_user_query
        self.voice_handler.start()
        logger.info("Voice handler started")

        # Start main loop
        self.running = True
        self._main_loop()

    def stop(self) -> None:
        """Stop ApexEngineer"""
        print("Stopping ApexEngineer...")
        self.running = False
        self.voice_handler.stop()
        self.telemetry_reader.disconnect()

    def _main_loop(self) -> None:
        """Main application loop"""
        print("ApexEngineer is running. Press Ctrl+C to stop.")
        print("Hold SPACE (or configured key) to talk to your engineer.")

        try:
            while self.running:
                # Update telemetry at configured rate
                current_time = time.time()
                if current_time - self.last_telemetry_update >= 1.0 / self.update_rate:
                    self._update_telemetry()
                    self.last_telemetry_update = current_time

                # Small sleep to prevent CPU spinning
                time.sleep(0.01)

        except KeyboardInterrupt:
            print("\nShutting down...")
            self.stop()

    def _update_telemetry(self) -> None:
        """Update telemetry data"""
        telemetry = self.telemetry_reader.read()
        if telemetry:
            self.context_engine.update(telemetry)

    def _handle_user_query(self, query: str) -> None:
        """
        Handle user voice query

        Args:
            query: Transcribed user query
        """
        if not query or not query.strip():
            logger.debug("Empty query received, ignoring")
            return

        logger.info(f"Received query: {query}")
        print(f"\nDriver: {query}")

        # Get current context
        logger.debug("Getting telemetry context...")
        context = self.context_engine.get_detailed_context()
        logger.debug(f"Context retrieved: {len(context)} keys")

        # Generate AI response
        logger.info("Generating AI response...")
        print("[AI] Thinking...", end="", flush=True)
        start_time = time.time()
        
        response = self.ai_module.generate_response(query, context)
        
        elapsed = time.time() - start_time
        logger.info(f"AI response generated in {elapsed:.2f}s")
        print(f"\r[AI] Response ready ({elapsed:.2f}s)")  # Clear the "Thinking..." line
        print(f"Engineer: {response}")

        # Speak response if TTS enabled
        if self.voice_handler.tts_enabled:
            logger.debug("Speaking response via TTS...")
            self.voice_handler.speak(response)


def main():
    """Main entry point"""
    app = ApexEngineer()
    app.start()


if __name__ == "__main__":
    main()


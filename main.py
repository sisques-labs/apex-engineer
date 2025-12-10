"""Main entry point for ApexEngineer"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ai import GPT4AllClient, OllamaClient
from src.config import ConfigManager
from src.telemetry import AssettoCorsaReader, ContextEngine
from src.voice import VoiceHandler


class ApexEngineer:
    """Main ApexEngineer application"""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize ApexEngineer"""
        self.config = ConfigManager(config_path)

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
        """Initialize AI module based on config"""
        ai_model = self.config.get("ai.model", "ollama")

        if ai_model == "ollama":
            return OllamaClient(
                endpoint=self.config.get("ai.endpoint", "http://localhost:11434"),
                model_name=self.config.get("ai.model_name", "llama2"),
                temperature=self.config.get("ai.temperature", 0.7),
                max_tokens=self.config.get("ai.max_tokens", 150),
            )
        elif ai_model == "gpt4all":
            return GPT4AllClient(
                model_name=self.config.get("ai.model_name", "ggml-gpt4all-j-v1.3-groovy.bin"),
                model_path=self.config.get("ai.model_path"),
                temperature=self.config.get("ai.temperature", 0.7),
                max_tokens=self.config.get("ai.max_tokens", 150),
                n_threads=self.config.get("ai.n_threads", 4),
            )
        else:
            raise ValueError(f"Unsupported AI model: {ai_model}. Use 'ollama' or 'gpt4all'")

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
        print("Starting ApexEngineer...")

        # Connect to telemetry
        if not self.telemetry_reader.connect():
            print("Warning: Could not connect to Assetto Corsa telemetry")
            print("Running in mock mode for development")

        # Check AI availability
        if not self.ai_module.is_available():
            print("Warning: AI module is not available")
            print("Make sure Ollama is running: ollama serve")

        # Setup voice handler
        self.voice_handler.on_transcription = self._handle_user_query
        self.voice_handler.start()

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
            return

        print(f"\nDriver: {query}")

        # Get current context
        context = self.context_engine.get_detailed_context()

        # Generate AI response
        response = self.ai_module.generate_response(query, context)
        print(f"Engineer: {response}")

        # Speak response if TTS enabled
        if self.voice_handler.tts_enabled:
            self.voice_handler.speak(response)


def main():
    """Main entry point"""
    app = ApexEngineer()
    app.start()


if __name__ == "__main__":
    main()


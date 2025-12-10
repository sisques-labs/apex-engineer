"""GPT4All client for local LLM interaction"""

import logging
import time
from typing import Any, Dict, Optional

from .ai_module import AIModule

logger = logging.getLogger(__name__)


class GPT4AllClient(AIModule):
    """Client for interacting with GPT4All local LLM"""

    def __init__(
        self,
        model_name: str = "mistral-7b-instruct-v0.1.Q4_0.gguf",
        model_path: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 150,
        n_threads: int = 4,
        language: str = "es",
    ):
        """
        Initialize GPT4All client

        Args:
            model_name: Name of the model file to use
            model_path: Optional path to model directory (defaults to GPT4All default)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
            n_threads: Number of threads for inference
            language: Language code for responses (es, en, fr, etc.)
        """
        self.model_name = model_name
        self.model_path = model_path
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.n_threads = n_threads
        self.language = language.lower()
        self.model = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialize GPT4All model"""
        try:
            from gpt4all import GPT4All

            logger.info(f"Initializing GPT4All with model: {self.model_name}")
            print(f"Initializing GPT4All with model: {self.model_name}")
            print("Note: First run will download the model automatically (~4GB). This may take a few minutes...")
            
            logger.debug(f"Model path: {self.model_path or 'default'}, Threads: {self.n_threads}")
            
            # GPT4All will automatically download the model if it doesn't exist
            # The model_path parameter is optional - if None, uses default GPT4All directory
            init_start = time.time()
            self.model = GPT4All(
                model_name=self.model_name,
                model_path=self.model_path,
                n_threads=self.n_threads,
            )
            init_time = time.time() - init_start
            
            logger.info(f"GPT4All model loaded successfully in {init_time:.2f}s")
            print(f"✓ GPT4All model '{self.model_name}' loaded successfully!")
            
        except ImportError:
            logger.error("GPT4All not installed")
            print("ERROR: GPT4All not installed.")
            print("Install with: pip install gpt4all")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to initialize GPT4All model: {e}", exc_info=True)
            print(f"ERROR: Failed to initialize GPT4All model: {e}")
            print(f"Model name: {self.model_name}")
            print("\nThis model may no longer be available. Try one of these alternatives:")
            print("  - mistral-7b-instruct-v0.1.Q4_0.gguf (recommended, ~4GB)")
            print("  - orca-mini-3b-gguf2-q4_0.gguf (smaller, faster, ~2GB)")
            print("  - llama-2-7b-chat.Q4_0.gguf (~4GB)")
            print("\nUpdate the 'model_name' in config.yaml with one of the above.")
            print("Check all available models at: https://gpt4all.io/index.html")
            print("\nMake sure you have internet connection for first-time model download.")
            import traceback
            traceback.print_exc()
            self.model = None

    def generate_response(
        self, user_query: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate AI response using GPT4All

        Args:
            user_query: User's question or command
            context: Optional telemetry context

        Returns:
            AI-generated response string
        """
        if not self.model:
            logger.error("Model not available for response generation")
            error_messages = {
                "es": "Modelo GPT4All no disponible. Verifica la instalación.",
                "en": "Sorry, GPT4All model is not available. Please check installation.",
                "fr": "Modèle GPT4All non disponible. Vérifiez l'installation.",
            }
            return error_messages.get(self.language, error_messages["en"])

        logger.debug("Building prompt with context...")
        # Build prompt with context
        prompt = self._build_prompt(user_query, context)
        logger.debug(f"Prompt length: {len(prompt)} characters")
        
        # Log the full prompt for debugging
        logger.debug("=" * 80)
        logger.debug("PROMPT SENT TO GPT4All:")
        logger.debug("-" * 80)
        logger.debug(prompt)
        logger.debug("-" * 80)
        logger.debug("=" * 80)

        try:
            logger.info("Starting GPT4All inference...")
            logger.debug(f"Parameters: temp={self.temperature}, max_tokens={self.max_tokens}, threads={self.n_threads}")
            
            # Generate response with maximum speed optimizations
            # Aggressive parameters for fastest possible generation
            gen_start = time.time()
            # Limit tokens aggressively for speed
            max_tokens_limited = min(self.max_tokens, 50)
            response = self.model.generate(
                prompt,
                streaming=False,
                temp=self.temperature,
                max_tokens=max_tokens_limited,
                top_k=10,  # Very low for faster generation
                top_p=0.5,  # Lower for faster, more deterministic
                repeat_penalty=1.05,  # Lower penalty for speed
                n_batch=512,  # Larger batch for better throughput
            )
            gen_time = time.time() - gen_start
            
            # Get language-specific error messages
            error_messages = {
                "es": "No pude generar una respuesta.",
                "en": "I couldn't generate a response.",
                "fr": "Je n'ai pas pu générer de réponse.",
            }
            default_error = error_messages.get(self.language, error_messages["en"])
            
            response_text = response.strip() if response else default_error
            logger.info(f"Inference completed in {gen_time:.2f}s, response length: {len(response_text)} chars")
            logger.debug(f"Response preview: {response_text[:100]}...")
            
            return response_text
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            print(f"Error generating response with GPT4All: {e}")
            
            # Language-specific error messages
            error_messages = {
                "es": "Problema técnico, repite la pregunta.",
                "en": "Technical issue, please repeat the question.",
                "fr": "Problème technique, répète la question.",
            }
            return error_messages.get(self.language, error_messages["en"])

    def _build_prompt(self, user_query: str, context: Optional[Dict[str, Any]]) -> str:
        """
        Build prompt with telemetry context (optimized for speed and configured language)

        Args:
            user_query: User's question
            context: Telemetry context dictionary

        Returns:
            Formatted prompt string
        """
        # Get language-specific prompt
        system_prompt = self._get_system_prompt()

        if context and "current" in context:
            context_summary = self._format_context(context)
            # Ultra-compact prompt format for speed
            prompt = f"""{system_prompt}
Data: {context_summary}
Q: {user_query}
A:"""
        else:
            prompt = f"""{system_prompt}

Q: {user_query}
A:"""

        return prompt

    def _get_system_prompt(self) -> str:
        """Get system prompt based on configured language (optimized for speed)"""
        prompts = {
            "es": """Eres ingeniero F1. Responde en español, 1-2 frases, directo y técnico.""",
            
            "en": """You are an F1 race engineer. Respond in English, 1-2 sentences, direct and technical.""",
            
            "fr": """Tu es ingénieur F1. Réponds en français, 1-2 phrases, direct et technique.""",
        }
        
        # Default to English if language not found
        return prompts.get(self.language, prompts["en"])

    def _format_context(self, context: Dict[str, Any]) -> str:
        """
        Format context dictionary into compact text for faster processing
        
        Data source:
        - If connected to Assetto Corsa: Real-time telemetry from shared memory
        - If not connected: Mock/test data (see assetto_corsa_reader._read_mock_data)
        """
        parts = []
        current = context.get("current", {})

        # Compact format: key:value pairs separated by commas
        # Current telemetry values
        if "speed" in current:
            parts.append(f"S:{current['speed']:.0f}")
        if "rpm" in current:
            parts.append(f"RPM:{current['rpm']}")
        if "gear" in current:
            parts.append(f"G:{current['gear']}")
        if "fuel" in current:
            parts.append(f"F:{current['fuel']:.1f}L")
        if "lap_time" in current and current.get("lap_time"):
            parts.append(f"Lap:{current['lap_time']:.1f}s")
        if "best_lap_time" in context and context["best_lap_time"]:
            parts.append(f"Best:{context['best_lap_time']:.1f}s")
        if "tire_temperatures" in current:
            temps = current["tire_temperatures"]
            parts.append(f"Tires:FL{temps.get('front_left', 0):.0f} FR{temps.get('front_right', 0):.0f} RL{temps.get('rear_left', 0):.0f} RR{temps.get('rear_right', 0):.0f}")
        
        # Include deltas if available (rate of change)
        deltas = context.get("deltas", {})
        if deltas:
            delta_parts = []
            if "speed" in deltas:
                delta_parts.append(f"ΔS:{deltas['speed']:+.1f}")
            if "rpm" in deltas:
                delta_parts.append(f"ΔRPM:{deltas['rpm']:+d}")
            if "fuel" in deltas:
                delta_parts.append(f"ΔF:{deltas['fuel']:.3f}L")
            if delta_parts:
                parts.append("Deltas:" + " ".join(delta_parts))
        
        # Include performance analysis if available
        analysis = context.get("analysis", {})
        if analysis:
            analysis_parts = []
            if "tire_temp_trend" in analysis:
                trend = analysis["tire_temp_trend"]
                analysis_parts.append(f"TireTrend:{trend}")
            if "fuel_consumption_rate" in analysis:
                rate = analysis["fuel_consumption_rate"]
                analysis_parts.append(f"FuelRate:{rate:.3f}L/s")
            if analysis_parts:
                parts.append("Analysis:" + " ".join(analysis_parts))
        
        # Position information if available
        if "position" in current:
            parts.append(f"Pos:P{current['position']}")

        formatted = ", ".join(parts)
        
        # Log data source for debugging
        if current.get("_is_mock"):
            logger.debug(f"[MOCK DATA] Telemetry: {formatted}")
        else:
            logger.debug(f"[REAL DATA] Telemetry: {formatted}")
        
        return formatted

    def is_available(self) -> bool:
        """
        Check if GPT4All is available

        Returns:
            True if model is loaded and ready, False otherwise
        """
        return self.model is not None


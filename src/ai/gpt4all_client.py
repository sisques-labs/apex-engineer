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

        try:
            logger.info("Starting GPT4All inference...")
            logger.debug(f"Parameters: temp={self.temperature}, max_tokens={self.max_tokens}, threads={self.n_threads}")
            
            # Generate response with optimized parameters for speed
            # Reduced top_k and top_p for faster generation
            gen_start = time.time()
            response = self.model.generate(
                prompt,
                streaming=False,
                temp=self.temperature,
                max_tokens=self.max_tokens,
                top_k=20,  # Reduced from 40 for faster generation
                top_p=0.7,  # Reduced from 0.9 for faster generation
                repeat_penalty=1.1,
                n_batch=512,  # Batch size for faster processing
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
            prompt = f"""{system_prompt}

Telemetría: {context_summary}

Piloto: {user_query}

Ingeniero:"""
        else:
            prompt = f"""{system_prompt}

Piloto: {user_query}

Ingeniero:"""

        return prompt

    def _get_system_prompt(self) -> str:
        """Get system prompt based on configured language"""
        prompts = {
            "es": """Eres un ingeniero de Fórmula 1 hablando por radio con tu piloto durante una carrera.
Responde SIEMPRE en español natural y directo, como lo haría un ingeniero real.
Sé conciso (1-2 frases máximo), técnico pero claro, y da consejos accionables.
Ejemplos de estilo:
- "Los neumáticos están bien, mantén el ritmo"
- "Ahorra combustible, reduce 200 rpm en rectas"
- "Estás 0.3s más lento, empuja más en la curva 3"
NO uses inglés mezclado. Habla como un ingeniero español profesional.""",
            
            "en": """You are a Formula 1 race engineer speaking over radio with your driver during a race.
Always respond in natural, direct English, as a real engineer would.
Be concise (1-2 sentences max), technical but clear, and give actionable advice.
Style examples:
- "Tyres are good, maintain pace"
- "Save fuel, reduce 200 rpm on straights"
- "You're 0.3s slower, push more in turn 3"
Speak like a professional F1 engineer.""",
            
            "fr": """Tu es un ingénieur de Formule 1 parlant à la radio avec ton pilote pendant une course.
Réponds TOUJOURS en français naturel et direct, comme le ferait un vrai ingénieur.
Sois concis (1-2 phrases max), technique mais clair, et donne des conseils actionnables.
Exemples de style:
- "Les pneus sont bons, maintiens le rythme"
- "Économise le carburant, réduis 200 tr/min en ligne droite"
- "Tu es 0.3s plus lent, pousse plus dans le virage 3"
Parle comme un ingénieur F1 professionnel.""",
        }
        
        # Default to English if language not found
        return prompts.get(self.language, prompts["en"])

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary into compact text for faster processing"""
        parts = []
        current = context.get("current", {})

        # Compact format: key:value pairs separated by commas
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

        return ", ".join(parts)

    def is_available(self) -> bool:
        """
        Check if GPT4All is available

        Returns:
            True if model is loaded and ready, False otherwise
        """
        return self.model is not None


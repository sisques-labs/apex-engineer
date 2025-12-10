"""GPT4All client for local LLM interaction"""

from typing import Any, Dict, Optional

from .ai_module import AIModule


class GPT4AllClient(AIModule):
    """Client for interacting with GPT4All local LLM"""

    def __init__(
        self,
        model_name: str = "ggml-gpt4all-j-v1.3-groovy.bin",
        model_path: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 150,
        n_threads: int = 4,
    ):
        """
        Initialize GPT4All client

        Args:
            model_name: Name of the model file to use
            model_path: Optional path to model directory (defaults to GPT4All default)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
            n_threads: Number of threads for inference
        """
        self.model_name = model_name
        self.model_path = model_path
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.n_threads = n_threads
        self.model = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialize GPT4All model"""
        try:
            from gpt4all import GPT4All

            self.model = GPT4All(
                model_name=self.model_name,
                model_path=self.model_path,
                n_threads=self.n_threads,
            )
        except ImportError:
            print("GPT4All not installed. Install with: pip install gpt4all")
            self.model = None
        except Exception as e:
            print(f"Error initializing GPT4All model: {e}")
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
            return "Sorry, GPT4All model is not available. Please check installation."

        # Build prompt with context
        prompt = self._build_prompt(user_query, context)

        try:
            # Generate response
            # GPT4All API: generate(prompt, streaming=False, **kwargs)
            response = self.model.generate(
                prompt,
                streaming=False,
                temp=self.temperature,
                max_tokens=self.max_tokens,
                top_k=40,
                top_p=0.9,
                repeat_penalty=1.1,
            )
            return response.strip() if response else "I couldn't generate a response."
        except Exception as e:
            print(f"Error generating response with GPT4All: {e}")
            return "Sorry, I'm having trouble generating a response."

    def _build_prompt(self, user_query: str, context: Optional[Dict[str, Any]]) -> str:
        """
        Build prompt with telemetry context

        Args:
            user_query: User's question
            context: Telemetry context dictionary

        Returns:
            Formatted prompt string
        """
        system_prompt = """You are a professional Formula 1 race engineer providing real-time advice to a driver during a race. 
You have access to live telemetry data and should provide concise, actionable feedback. 
Keep responses brief (under 50 words) and focused on immediate actions or insights."""

        if context and "current" in context:
            context_summary = self._format_context(context)
            prompt = f"""{system_prompt}

Current Race Data:
{context_summary}

Driver Question: {user_query}

Engineer Response:"""
        else:
            prompt = f"""{system_prompt}

Driver Question: {user_query}

Engineer Response:"""

        return prompt

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary into readable text"""
        lines = []
        current = context.get("current", {})

        if "speed" in current:
            lines.append(f"Speed: {current['speed']:.1f} km/h")
        if "rpm" in current:
            lines.append(f"RPM: {current['rpm']}")
        if "gear" in current:
            lines.append(f"Gear: {current['gear']}")
        if "fuel" in current:
            lines.append(f"Fuel: {current['fuel']:.1f}L")
        if "lap_time" in current and current.get("lap_time"):
            lines.append(f"Lap time: {current['lap_time']:.2f}s")
        if "best_lap_time" in context and context["best_lap_time"]:
            lines.append(f"Best lap: {context['best_lap_time']:.2f}s")
        if "tire_temperatures" in current:
            temps = current["tire_temperatures"]
            lines.append(
                f"Tire temps: FL:{temps.get('front_left', 0):.0f}°C FR:{temps.get('front_right', 0):.0f}°C RL:{temps.get('rear_left', 0):.0f}°C RR:{temps.get('rear_right', 0):.0f}°C"
            )

        return "\n".join(lines)

    def is_available(self) -> bool:
        """
        Check if GPT4All is available

        Returns:
            True if model is loaded and ready, False otherwise
        """
        return self.model is not None


"""Ollama client for local LLM interaction"""

from typing import Any, Dict, Optional

import requests

from .ai_module import AIModule


class OllamaClient(AIModule):
    """Client for interacting with Ollama local LLM"""

    def __init__(
        self,
        endpoint: str = "http://localhost:11434",
        model_name: str = "llama2",
        temperature: float = 0.7,
        max_tokens: int = 150,
    ):
        """
        Initialize Ollama client

        Args:
            endpoint: Ollama API endpoint URL
            model_name: Name of the model to use
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
        """
        self.endpoint = endpoint.rstrip("/")
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_url = f"{self.endpoint}/api/generate"

    def generate_response(
        self, user_query: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate AI response using Ollama

        Args:
            user_query: User's question or command
            context: Optional telemetry context

        Returns:
            AI-generated response string
        """
        # Build prompt with context
        prompt = self._build_prompt(user_query, context)

        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens,
                    },
                },
                timeout=5,
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "I couldn't generate a response.")
        except requests.exceptions.RequestException as e:
            print(f"Error calling Ollama API: {e}")
            return "Sorry, I'm having trouble connecting to the AI model."

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
            lines.append(f"Tire temps: FL:{temps.get('front_left', 0):.0f}°C FR:{temps.get('front_right', 0):.0f}°C RL:{temps.get('rear_left', 0):.0f}°C RR:{temps.get('rear_right', 0):.0f}°C")

        return "\n".join(lines)

    def is_available(self) -> bool:
        """
        Check if Ollama is available

        Returns:
            True if Ollama is reachable, False otherwise
        """
        try:
            response = requests.get(f"{self.endpoint}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False


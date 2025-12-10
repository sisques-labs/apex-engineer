"""AI module for local LLM interaction"""

from .ai_module import AIModule
from .gpt4all_client import GPT4AllClient
from .ollama_client import OllamaClient

__all__ = ["AIModule", "GPT4AllClient", "OllamaClient"]


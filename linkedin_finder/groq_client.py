"""
Groq API client for LinkedIn Finder

This module provides a general interface to the Groq API for various AI tasks.
Users can provide their own API key or use environment variables.
"""

import os
from typing import Optional, Dict, Any, List
import json
import logging
from dataclasses import dataclass

try:
    from groq import Groq
except ImportError:
    Groq = None

logger = logging.getLogger(__name__)


@dataclass
class GroqResponse:
    """Response from Groq API"""

    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    success: bool = True
    error: Optional[str] = None


class GroqClient:
    """
    General-purpose Groq API client

    Supports multiple models and provides a unified interface for AI tasks.
    """

    # Available models (fast and cheap options)
    MODELS = {
        "llama-3.1-8b-instant": "Fast 8B parameter model, good for simple tasks",
        "llama-3.1-70b-versatile": "Larger model for complex reasoning",
        "mixtral-8x7b-32768": "Mixtral model with large context window",
    }

    def __init__(
        self, api_key: Optional[str] = None, model: str = "llama-3.1-8b-instant"
    ):
        """
        Initialize Groq client

        Args:
            api_key: Groq API key. If None, will try to load from GROQ_API_KEY env var
            model: Model to use for requests
        """
        if Groq is None:
            raise ImportError(
                "Groq library not installed. Install with: pip install groq"
            )

        # Try to get API key from parameter, env var, or .env file
        self.api_key = api_key or self._load_api_key()
        if not self.api_key:
            raise ValueError(
                "Groq API key not found. Provide via api_key parameter or set GROQ_API_KEY environment variable"
            )

        self.model = model
        self.client = Groq(api_key=self.api_key)

        logger.debug(f"Initialized Groq client with model: {model}")

    def _load_api_key(self) -> Optional[str]:
        """Load API key from environment or .env file"""
        # First try environment variable
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            return api_key

        # Try to load from .env file in project root
        try:
            # Go up to project root (linkedin_finder -> project root)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            env_file = os.path.join(project_root, ".env")

            if os.path.exists(env_file):
                with open(env_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GROQ_API_KEY="):
                            return line.split("=", 1)[1].strip()
        except Exception as e:
            logger.debug(f"Could not load .env file: {e}")

        return None

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
    ) -> GroqResponse:
        """
        Create a chat completion

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            model: Model to use (overrides default)

        Returns:
            GroqResponse with the completion
        """
        try:
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            content = response.choices[0].message.content
            usage = (
                response.usage._asdict() if hasattr(response.usage, "_asdict") else None
            )

            return GroqResponse(
                content=content, model=response.model, usage=usage, success=True
            )

        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return GroqResponse(
                content="", model=model or self.model, success=False, error=str(e)
            )

    def simple_prompt(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
    ) -> GroqResponse:
        """
        Simple prompt interface

        Args:
            prompt: The user prompt
            system_message: Optional system message
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            GroqResponse with the completion
        """
        messages = []

        if system_message:
            messages.append({"role": "system", "content": system_message})

        messages.append({"role": "user", "content": prompt})

        return self.chat_completion(
            messages=messages, temperature=temperature, max_tokens=max_tokens
        )

    def is_available(self) -> bool:
        """Check if Groq API is available and working"""
        try:
            response = self.simple_prompt("Test", max_tokens=1)
            return response.success
        except Exception:
            return False


# Convenience function for quick access
def create_groq_client(
    api_key: Optional[str] = None, model: str = "llama-3.1-8b-instant"
) -> Optional[GroqClient]:
    """
    Create a Groq client with error handling

    Returns None if Groq is not available or API key is missing
    """
    try:
        return GroqClient(api_key=api_key, model=model)
    except Exception as e:
        logger.warning(f"Could not create Groq client: {e}")
        return None

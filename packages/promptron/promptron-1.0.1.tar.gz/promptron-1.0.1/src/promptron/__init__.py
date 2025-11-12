"""Promptron - A Python package for generating evaluation datasets using LLMs."""

__version__ = "1.0.1"

from promptron.prompt_generator import generate_prompts
from promptron.llm_config import LLMConfig

__all__ = ["generate_prompts", "LLMConfig", "__version__"]


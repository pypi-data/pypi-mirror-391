"""
seraa/llm - LLM integration for natural language ethics
"""

from .ethical_agent import EthicalLLMAgent
from .chat_agent import SeraaChat

__all__ = ['EthicalLLMAgent', 'SeraaChat']

pac_minimum: float = 0.4,
harm_threshold: int = 2,
transparency_min: float = 0.5

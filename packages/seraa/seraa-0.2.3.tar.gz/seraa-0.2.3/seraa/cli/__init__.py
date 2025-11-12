"""
seraa/cli - Command-line interfaces for SERAA
"""

from .chat import main as chat_main
from .evaluate import main as evaluate_main

__all__ = ['chat_main', 'evaluate_main']

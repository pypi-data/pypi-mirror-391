"""
ORATIO - L'Eloquenza del Codice

Dove le parole diventano azioni.
"""

__version__ = "0.1.0"
__author__ = "Manuel Lazzaro"
__description__ = "ORATIO - The Eloquence of Code"

from .compiler import SemanticParser
from .runtime import Runtime

__all__ = ["SemanticParser", "Runtime"]

"""
Sigil Data Workspace - Rule Zero Compliant Data Processing

A comprehensive workspace for data processing with Sacred Chain traceability,
AI integration, and complete audit capabilities.
"""

__version__ = "1.4.1"
__author__ = "Rule Zero Compliant Developer"

from .core.config import SacredChainConfig, WorkspaceConfig
from .core.pipeline import DataPipeline
from .core.sacred_chain import ChainLink, SacredChain
from .processors.ai_processor import AIProcessor
from .processors.base import BaseProcessor
from .processors.validator import DataValidator

__all__ = [
    "DataPipeline",
    "WorkspaceConfig",
    "SacredChainConfig",
    "SacredChain",
    "ChainLink",
    "BaseProcessor",
    "AIProcessor",
    "DataValidator",
]

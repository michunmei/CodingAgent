"""
Multi-Agent Collaborative System for Automated Software Development
COMP7103C Code Agent Building Assignment

This system uses the Qwen LLM family for multi-agent collaboration
in automated software development workflows.
"""

__version__ = "1.0.0"
__author__ = "COMP7103C Student"
__description__ = "Multi-Agent Collaborative System using Qwen LLM"

from .config import Config
from .core.orchestrator import MultiAgentOrchestrator
from .core.llm_provider import QwenProvider, LLMInterface
from .agents.base_agent import ProjectPlanningAgent, CodeGenerationAgent, CodeEvaluationAgent, ProjectContext
from .tools.filesystem_tools import FileSystemTools, WebSearchTool

__all__ = [
    "Config",
    "MultiAgentOrchestrator", 
    "QwenProvider",
    "LLMInterface",
    "ProjectPlanningAgent",
    "CodeGenerationAgent", 
    "CodeEvaluationAgent",
    "ProjectContext",
    "FileSystemTools",
    "WebSearchTool"
]
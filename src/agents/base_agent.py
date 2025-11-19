# src/agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json


class BaseAgent(ABC):
    """Base class for all agents"""

    def __init__(self, name: str, gemini_model=None):
        self.name = name
        self.gemini_model = gemini_model
        self.history = []

    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """The main method of performing the agent's task."""
        pass

    def log(self, message: str):
        """Logging actions"""

        print(f"[{self.name}] {message}")
        self.history.append(message)

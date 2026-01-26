from abc import ABC, abstractmethod
from typing import Dict, Any, List


class FeedbackProvider(ABC):
    """Collects feedback from executions, users, systems, governance, audits"""

    @abstractmethod
    def collect(self, context, event: Dict[str, Any]) -> Dict[str, Any]:
        pass


class OutcomeEvaluator(ABC):
    """Evaluates success/failure/quality/risk of outcomes"""

    @abstractmethod
    def evaluate(self, event: Dict[str, Any]) -> Dict[str, Any]:
        pass


class PatternDetector(ABC):
    """Detects patterns across learning memory"""

    @abstractmethod
    def detect(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        pass


class ExperienceWeighter(ABC):
    """Weights experiences over time"""

    @abstractmethod
    def weight(self, event: Dict[str, Any], history: List[Dict[str, Any]]) -> float:
        pass


class BehaviorShaper(ABC):
    """Transforms learning into behavior influence"""

    @abstractmethod
    def shape(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        pass


class AdaptationRule(ABC):
    """Defines system adaptation logic"""

    @abstractmethod
    def apply(self, state: Dict[str, Any], learning: Dict[str, Any]) -> Dict[str, Any]:
        pass


class ReinforcementModel(ABC):
    """Reinforcement logic for decisions"""

    @abstractmethod
    def reinforce(self, decision: Dict[str, Any], outcome: Dict[str, Any]) -> Dict[str, Any]:
        pass

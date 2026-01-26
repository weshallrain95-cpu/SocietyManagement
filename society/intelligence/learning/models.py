from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime


@dataclass
class LearningEvent:
    timestamp: datetime
    source: str
    node_id: str
    workflow_id: str | None
    event_type: str
    payload: Dict[str, Any]
    scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class LearningInsight:
    patterns: Dict[str, Any]
    risks: Dict[str, float]
    confidence: Dict[str, float]
    recommendations: Dict[str, Any]
    adaptations: Dict[str, Any]

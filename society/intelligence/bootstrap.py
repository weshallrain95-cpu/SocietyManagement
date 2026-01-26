from society.intelligence.engine import IntelligenceEngine
from society.intelligence.learning.engine import LearningEngine


def build_intelligence():
    """
    Bootstrap the full intelligence stack:
    - Intelligence core
    - Learning engine
    - Memory integration
    """

    # Core intelligence engine
    engine = IntelligenceEngine()

    # Learning engine (with persistent memory adapter)
    learning_engine = LearningEngine()

    # Attach learning to intelligence
    engine.learning = learning_engine

    return engine

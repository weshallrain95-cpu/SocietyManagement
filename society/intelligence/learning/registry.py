class LearningRegistry:
    feedback_providers = []
    evaluators = []
    detectors = []
    weighters = []
    shapers = []
    adaptation_rules = []
    reinforcement_models = []

    @classmethod
    def register_feedback(cls, obj):
        cls.feedback_providers.append(obj)

    @classmethod
    def register_evaluator(cls, obj):
        cls.evaluators.append(obj)

    @classmethod
    def register_detector(cls, obj):
        cls.detectors.append(obj)

    @classmethod
    def register_weighter(cls, obj):
        cls.weighters.append(obj)

    @classmethod
    def register_shaper(cls, obj):
        cls.shapers.append(obj)

    @classmethod
    def register_adaptation(cls, obj):
        cls.adaptation_rules.append(obj)

    @classmethod
    def register_reinforcement(cls, obj):
        cls.reinforcement_models.append(obj)

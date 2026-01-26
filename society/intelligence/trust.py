class TrustEngine:
    def score(self, actor: str | None) -> float:
        raise NotImplementedError

from .engine import Engine


class MatchingEngineService(Engine):
    name: str = "matching_engine"

    def __init__(self):
        super().__init__()

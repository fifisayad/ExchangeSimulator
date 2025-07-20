from ..repository import PositionRepository


class PositionService:

    def __init__(self) -> None:
        self.position_repo = PositionRepository()

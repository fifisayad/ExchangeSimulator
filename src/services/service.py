from abc import ABC, abstractmethod

from fifi import DecoratedBase, Repository
from pydantic import BaseModel


class Service(ABC):
    @property
    @abstractmethod
    def repo(self) -> Repository:
        pass

    async def create(self, data: BaseModel) -> DecoratedBase:
        return await self.repo.create(data=data)

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

from fifi import DecoratedBase, Repository
from pydantic import BaseModel


EntityModel = TypeVar("EntityModel", bound=DecoratedBase)
EntitySchema = TypeVar("EntitySchema", bound=BaseModel)


class Service(ABC, Generic[EntityModel, EntitySchema]):
    @property
    @abstractmethod
    def repo(self) -> Repository:
        pass

    async def create(self, data: EntitySchema) -> EntityModel:
        return await self.repo.create(data=data)

    async def create_many(self, data: List[EntitySchema]) -> List[EntityModel]:
        return await self.repo.create_many(data=data)

    async def read_by_id(self, id: str) -> Optional[EntityModel]:
        return await self.repo.get_one_by_id(id_=id)

    async def read_many_by_ids(self, ids: List[str]) -> List[EntityModel]:
        return await self.repo.get_many_by_ids(ids=ids)

    async def update_entity(self, entity: EntityModel) -> None:
        return await self.repo.update_entity(entity=entity)

    async def update_by_id(self, id: str, data: EntitySchema) -> EntityModel:
        return await self.update_by_id(id=id, data=data)

    async def update_many_by_ids(
        self, ids: List[str], data: List[EntitySchema]
    ) -> List[EntityModel]:
        return await self.update_many_by_ids(ids=ids, data=data)

    async def remove_by_id(self, id: str) -> int:
        return await self.remove_by_id(id=id)

    async def remove_many_by_ids(self, ids: List[str]) -> int:
        return await self.remove_many_by_ids(ids=ids)

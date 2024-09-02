from abc import abstractmethod
from dataclasses import dataclass
from typing import Type

from sqlalchemy import select

from Repo import CRUDRepositoryInterface
from database import async_session_maker


@dataclass
class AbstractSQLAlchemyRepository[Entity, Model, CreateDTO, UpdateDTO](
    CRUDRepositoryInterface[Model, CreateDTO, UpdateDTO]
):
    session_maker: async_session_maker

    def __post_init__(self):
        self.entity: Type[Entity] = self.__orig_bases__[0].__args__[0]

    async def create(self, obj: CreateDTO) -> None:
        async with self.session_maker() as session:
            async with session.begin():
                session.add(self.model_to_entity(obj))

            obj = (await session.execute(select(self.entity).filter_by(**obj.model_dump()))).scalars().first()
        return self.entity_to_model(obj)

    async def get(self, obj_id: int) -> Model:
        async with self.session_maker() as session:
            res = await session.get(self.entity, obj_id)
            return self.entity_to_model(res)

    async def update(self, obj_id: int, obj: UpdateDTO) -> None:
        async with self.session_maker() as session:
            async with session.begin():
                entity = await session.get(self.entity, obj_id)
                for key, value in obj.__dict__.items():
                    setattr(entity, key, value)
            obj = (await session.execute(select(self.entity).filter_by(id=obj_id))).scalars().first()
        return self.entity_to_model(obj)

    async def delete(self, obj_id: int) -> None:
        async with self.session_maker() as session:
            async with session.begin():
                obj = await session.get(self.entity, obj_id)
                if obj:
                    await session.delete(obj)

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Model]:
        async with self.session_maker() as session:
            return [
                self.entity_to_model(entity)
                for entity in (await session.execute(
                    select(self.entity)
                    .limit(limit)
                    .offset(offset)
                )).scalars().all()
            ]

    async def get_filtered_by(self, **kwargs) -> list[Model]:
        async with self.session_maker() as session:
            return [
                self.entity_to_model(entity)
                for entity in (await session.execute(
                    select(self.entity)
                    .filter_by(**kwargs)
                )).scalars().all()
            ]

    @abstractmethod
    def entity_to_model(self, entity: Entity) -> Model:
        pass

    @abstractmethod
    def model_to_entity(self, model: Model) -> Entity:
        pass

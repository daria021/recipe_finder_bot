from abc import ABC, abstractmethod
from typing import TypeVar, List

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

Schema = TypeVar("Schema", bound=BaseModel, covariant=True)
SQLModel = TypeVar("SQLModel", bound=DeclarativeMeta, covariant=True)


class AbstractRepoInterface(ABC):

    @classmethod
    @abstractmethod
    async def get(cls, session: AsyncSession, record_id: int) -> Schema | None:
        ...

    @classmethod
    @abstractmethod
    async def get_all(cls, session: AsyncSession, *filters, offset: int = 0, limit: int = 100) -> List[Schema]:
        ...

    @classmethod
    @abstractmethod
    async def get_filtered_by(cls, session: AsyncSession, **kwargs) -> List[Schema]:
        ...

    @classmethod
    @abstractmethod
    async def create(cls, session: AsyncSession, **kwargs) -> Schema:
        ...

    @classmethod
    @abstractmethod
    async def update(cls, session: AsyncSession, record_id: int, **kwargs) -> Schema:
        ...

    @classmethod
    @abstractmethod
    async def delete(cls, session: AsyncSession, record_id: int):
        ...

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...

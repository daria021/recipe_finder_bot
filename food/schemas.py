from typing import Optional

from pydantic import BaseModel


class FoodCreate(BaseModel):
    title: str
    price: float


class FoodResponse(FoodCreate):
    id: int
    title: str
    price: float


class FoodUpdate(BaseModel):
    title: Optional[str]
    price: Optional[float]


class FoodFilter(BaseModel):
    title: Optional[str]
    price: Optional[float]

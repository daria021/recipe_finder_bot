from typing import Optional

from pydantic import BaseModel


class RecipeCreate(BaseModel):
    title: str
    description: str
    ingredients: list[str]


class RecipeResponse(RecipeCreate):
    id: int


class RecipeUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    ingredients: Optional[list[str]]


class RecipeFilter(BaseModel):
    title: str
    description: str
    ingredients: list[str]

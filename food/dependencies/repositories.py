from database import async_session_maker
from food.repository import FoodRepo


def get_food_repo() -> FoodRepo:
    return FoodRepo(session_maker=async_session_maker)

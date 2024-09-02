from food.dependencies.repositories import get_food_repo
from food.food_service import FoodService


def get_food_service():
    return FoodService(
        foods=get_food_repo()
    )

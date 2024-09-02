from GPT.GPTService import GPTService
from food.dependencies.repositories import get_food_repo


def get_gpt_service():
    return GPTService(foods=get_food_repo())

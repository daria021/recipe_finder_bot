from food.dependencies.repositories import get_food_repo
from recipe.dependencies.repositories import get_recipe_repo
from recipe.recipe_service import RecipeService


def get_recipe_service():
    return RecipeService(recipes=get_recipe_repo(), foods=get_food_repo())

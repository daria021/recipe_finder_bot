from database import async_session_maker
from recipe.repository import RecipeRepo


def get_recipe_repo() -> RecipeRepo:
    return RecipeRepo(session_maker=async_session_maker)
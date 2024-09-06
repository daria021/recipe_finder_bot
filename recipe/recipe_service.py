from dataclasses import dataclass

from food.repository import FoodRepo
from recipe.repository import RecipeRepo
from recipe.schemas import RecipeResponse


@dataclass
class RecipeService:
    recipes: RecipeRepo
    foods: FoodRepo

    async def get(self, id: int) -> RecipeResponse:
        recipe = await self.recipes.get(id)
        return recipe

    async def get_recipe_by_title(self, title: str) -> RecipeResponse:
        recipe = await self.recipes.get_filtered_by(title=title)
        return recipe[0]

    async def get_menu(self) -> list[RecipeResponse]:
        recipes = await self.recipes.get_all()
        foods = [x.title for x in await self.foods.get_all()]
        available_recipes = []
        for recipe in recipes:
            available = True
            for ingredient in recipe.ingredients:
                if not ingredient in foods:
                    available = False
                    break
            if available:
                available_recipes.append(recipe)

        return available_recipes

    async def get_recipes_by_ingredients(self, ingredients: list[str]):
        ingredients = list(map(str.lower, ingredients))
        recipe = list(filter(lambda x: all([ingredient in map(str.lower, x.ingredients) for ingredient in ingredients]),
                             await self.recipes.get_all()))
        return recipe

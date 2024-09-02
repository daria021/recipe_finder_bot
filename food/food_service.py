from dataclasses import dataclass

from food.repository import FoodRepo


@dataclass
class FoodService:
    foods: FoodRepo

    async def delete_all_food(self):
        all_food = await self.foods.get_all()
        for food in all_food:
            await self.foods.delete(food.id)

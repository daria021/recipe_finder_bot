from dataclasses import dataclass

from openai import AsyncOpenAI

from config import config
from food.repository import FoodRepo


@dataclass
class GPTService:
    foods: FoodRepo

    async def get_gpt_recipes(self):
        client = AsyncOpenAI(api_key=config.api_key, max_retries=5)
        food = await self.foods.get_all()
        ingredients = [x.title for x in food]
        response = await client.chat.completions.create(
            model="gpt-4o",
            temperature=0.5,
            messages=[
                {
                    "role": "user",
                    "content": f"придумай рецепт из этих ингредиентов: {ingredients}."
                }
            ],
        )
        response = response.model_dump()['choices'][0]['message']['content']
        return response

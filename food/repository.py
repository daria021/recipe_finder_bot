from Repo.AbstractRepository import AbstractSQLAlchemyRepository
from food.models import Food
from food.schemas import FoodUpdate, FoodCreate, FoodResponse


class FoodRepo(
    AbstractSQLAlchemyRepository[
        Food,
        FoodResponse,
        FoodCreate,
        FoodUpdate,
    ]
):
    def entity_to_model(self, entity: Food) -> FoodResponse:
        return FoodResponse(
            id=entity.id,
            title=entity.title,
            price=entity.price,
        )

    def model_to_entity(self, model: FoodResponse) -> Food:
        return Food(
            title=model.title,
            price=model.price,
        )

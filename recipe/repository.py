from Repo.AbstractRepository import AbstractSQLAlchemyRepository
from recipe.models import Recipe
from recipe.schemas import RecipeResponse, RecipeCreate, RecipeUpdate


class RecipeRepo(
    AbstractSQLAlchemyRepository[
        Recipe,
        RecipeResponse,
        RecipeCreate,
        RecipeUpdate,
    ]
):

    def entity_to_model(self, entity: Recipe) -> RecipeResponse:
        return RecipeResponse(
            id=entity.id,
            title=entity.title,
            ingredients=entity.ingredients,
            description=entity.description,
        )

    def model_to_entity(self, model: RecipeResponse) -> Recipe:
        return Recipe(
            title=model.title,
            ingredients=model.ingredients,
            description=model.description,
        )

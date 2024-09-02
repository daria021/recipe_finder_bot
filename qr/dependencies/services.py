from food.dependencies.repositories import get_food_repo
from qr.QRService import QRService


def get_qr_service():
    return QRService(food_repo=get_food_repo())

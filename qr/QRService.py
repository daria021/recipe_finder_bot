import logging
import os
from dataclasses import dataclass

from pyzbar.pyzbar import decode
from PIL import Image
import json
import requests

from food.repository import FoodRepo
from food.schemas import FoodCreate

logger = logging.getLogger(__name__)


@dataclass
class QRService:
    food_repo: FoodRepo

    async def decode_qr_code(self, image_path):
        # try:
        img = Image.open(image_path)

        decoded_objects = decode(img)

        logger.info(f"Decoded objects: {decoded_objects}")

        if decoded_objects:
            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                print("Данные, закодированные в QR-коде:", qr_data)
                products = await self.get_receipt_info(qr_data, image_path)
                return products

        else:
            logger.error("QR-код не найден или не удалось его декодировать.")
            return None



    async def get_receipt_info(self, qr_data: str, image_path: str):

        url = "https://proverkacheka.com/api/v1/check/get"
        data = {
            "token": "28592.HWUu8Tm5x4NUR3IjK",
            "qrraw": qr_data,
        }

        files = {"qrfile": open(image_path, "rb")}
        r = requests.post(url, data=data, files=files)
        os.remove(image_path)
        logger.info(f"Response from proverkacheka.com: {r.text}")
        products = await self.get_groseries(r.text)
        return products

    async def get_groseries(self, data: str):
        parsed_data = json.loads(data)
        logger.info(f"Decoded data: {parsed_data}")

        # Извлекаем названия продуктов
        product_names = [item['name'] for item in parsed_data['data']['json']['items']]
        product_prices = [item['sum'] / 100 for item in parsed_data['data']['json']['items']]

        for item in range(len(product_names)):
            schema = FoodCreate(title=product_names[item], price=product_prices[item])
            await self.food_repo.create(schema)

        return product_names


if __name__ == '__main__':
    qr_service = QRService()
    qr_service.decode_qr_code("./photo_2024-08-20 14.10.59.jpeg")

from typing import List

import redis
from django.conf import settings

from .models import Product

r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)


class Recommender:
    def get_product_key(self, id: int) -> str:
        """
        Generate a Redis key for a product.

        Args:
            id (int): The ID of the product.

        Returns:
            str: The Redis key for the product.

        """
        return f'product:{id}:purchased_with'

    def products_bought(self, products: List[object]) -> None:
        """
        Update the Redis sorted sets for products bought together. This method increments the score
        of products bought together in Redis.

        Args:
            products (List[object]): A list of product objects. Each product object must have an
            'id' attribute.

        """
        product_ids = [p.id for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                if product_id != with_id:
                    r.zincrby(self.get_product_key(product_id), 1, with_id)

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

    def suggest_products_for(self, products: List[Product], max_results: int = 6) -> List[Product]:
        """
        Suggest products for a given list of products.

        This method takes a list of products and returns a list of suggested products with scores
        based on the input products.

        Args:
            products (list): A list of Product objects for which suggestions are to be made.
            max_results (int, optional): The maximum number of suggested products to return.

        Returns:
            list: A list of suggested Product objects.

        """
        product_ids = [p.id for p in products]

        if len(products) == 1:
            suggestions = r.zrange(
                self.get_product_key(product_ids[0]), 0, -1, desc=True)[:max_results]
        else:
            flat_ids = ''.join([str(id) for id in product_ids])
            tmp_key = f'tmp_{flat_ids}'
            keys = [self.get_product_key(id) for id in product_ids]
            r.zunionstore(tmp_key, keys)
            r.zrem(tmp_key, *product_ids)
            suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_results]
            r.delete(tmp_key)

        suggested_products_ids = [int(id) for id in suggestions]
        suggested_products = list(Product.objects.filter(id__in=suggested_products_ids))
        suggested_products.sort(key=lambda x: suggested_products_ids.index(x.id))
        return suggested_products

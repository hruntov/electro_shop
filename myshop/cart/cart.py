from decimal import Decimal
from typing import Any, Dict

from django.conf import settings
from django.http import HttpRequest

from myshop.shop.models import Product


class Cart:
    """
    A shopping cart class for managing the shopping cart stored in the session.

    Attributes:
        session (SessionStore): The session object associated with the current user/request.
        cart (Dict[str, Any]): A dictionary representing the shopping cart items, loaded from the
            session.

    """
    def __init__(self, request: HttpRequest) -> None:
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product: Any, quantity: int = 1, override_quantity: bool = False) -> None:
        """
        Adds a product to the cart or updates its quantity.

        Args:
            product (Any): The product instance to add or update in the cart.
            quantity (int, optional): The amount of product to add or set.
            override_quantity (bool, optional): If True, the product quantity is set to `quantity`.
                If False, `quantity` is added to the existing quantity.

    """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self) -> None:
        """
        Marks the session as modified to ensure the cart is saved.
        """
        self.session.modified = True

    def remove(self, product) -> None:
        """
        Removes a product from the cart.

        Args:
            product (Any): The product instance to remove from the cart.

        """
        product_id = str(product.id)
        if product_id on self.cart:
            del self.cart[product_id]
            self.save()

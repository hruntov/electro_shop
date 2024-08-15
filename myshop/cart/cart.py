from decimal import Decimal
from typing import Any, Dict, Iterator, Optional

from django.conf import settings
from django.http import HttpRequest

from coupons.models import Coupon
from shop.models import Product


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
        self.coupon_id = self.session.get('coupon_id')

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """
        Iterates over the items in the cart, adding product details and calculating the total price.

        Yields:
            Iterator[Dict[str, Any]]: An iterator over the cart items, where each item is a
                dictionary containing product details, its price, quantity, and the total price.

        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self) -> int:
        """
        Calculates the total number of items in the cart.

        Returns:
            int: The total quantity of all items in the cart.

        """
        return sum(item['quantity'] for item in self.cart.values())

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
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def get_total_price(self) -> Decimal:
        """
        Calculates the total price of all items in the cart.

        Returns:
            Decimal: The total price of all items in the cart.

        """
        total = sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
        return Decimal(total)

    def clear(self) -> None:
        """Clears all items from the cart session."""
        del self.session[settings.CART_SESSION_ID]
        self.save()

    @property
    def coupon(self) -> Optional[Coupon]:
        """Returns the Coupon object if the coupon_id is valid, otherwise returns None."""
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self) -> Decimal:
        """Calculates the discount amount based on the coupon's discount percentage."""
        if self.coupon:
            return (self.coupon.discount / Decimal(100)) * self.get_total_price()
        return Decimal(0)

    def get_total_price_after_discount(self) -> Decimal:
        """Calculates the total price after applying the discount."""
        return self.get_total_price() - self.get_discount()

from decimal import Decimal
from typing import Union

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from coupons.models import Coupon
from shop.models import Product


class Order(models.Model):
    """Stores information about an order, including customer personal details and payment status."""
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    order_reference = models.CharField(null=True, blank=True)
    coupon = models.ForeignKey(Coupon, related_name='orders', null=True, blank=True,
                               on_delete=models.SET_NULL)
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0),
                                                          MaxValueValidator(100)])

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'

    def __str__(self) -> str:
        return f'Order {self.id}'

    def get_total_cost(self) -> Union[float, int]:
        """Calculates the total cost of the order."""
        total_cost = self.get_total_cost_before_discount()
        return total_cost - self.get_discount()

    def get_total_cost_before_discount(self) -> Decimal:
        """
        Calculate the total cost of items in the cart before applying any discounts.

        Returns:
            Decimal: The total cost of all items in the cart before any discounts.

        """
        return sum(item.get_cost() for item in self.items.all())

    def get_discount(self) -> Decimal:
        """
        Calculate the discount amount based on the total cost before discount.

        Returns:
            Decimal: The discount amount. Returns 0 if no discount is available.

        """
        total_cost = self.get_total_cost_before_discount()
        if self.discount:
            return total_cost * (self.discount / Decimal(100))
        return Decimal(0)


class OrderItem(models.Model):
    """Stores information about an individual item in an order, including price and quantity."""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Товар замовлення'
        verbose_name_plural = 'Товари замовлення'

    def __str__(self) -> str:
        return str(self.id)

    def get_cost(self) -> float:
        """Calculates the cost of the item by multiplying the price by the quantity."""
        return self.price * self.quantity

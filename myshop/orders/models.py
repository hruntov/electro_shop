from typing import Union

from django.db import models

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
        """Calculates the total cost of the order by summing the cost of each item in the order."""
        return sum(item.get_cost() for item in self.items.all())


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

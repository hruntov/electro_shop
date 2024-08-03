from typing import Dict

from django.http import HttpRequest

from .cart import Cart


def cart(request: HttpRequest) -> Dict[str, Cart]:
    """
    This context processor adds the cart instance to the context, making it available in all
        templates.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Dict[str, Cart]: A dictionary containing the cart instance.

    """
    return {'cart': Cart(request)}

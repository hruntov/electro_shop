from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import CartAddProductForm
from myshop.shop.models import Product


@require_POST
def cart_add(request, product_id) -> HttpResponseRedirect:
    """
    Adds a product to the cart or updates its quantity.

    Args:
        request (HttpRequest): The request object used to access session data.
        product_id (int): The ID of the product to add or update in the cart.

    Returns:
        HttpResponseRedirect: Redirects to the cart detail page.

    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product, quantity=cd['quanity'], override_quantity=cd['override'])

    return redirect('card:cart_detail')

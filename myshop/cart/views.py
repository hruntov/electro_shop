from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from shop.models import Product

from .cart import Cart
from .forms import CartAddProductForm


@require_POST
def cart_add(request: HttpRequest, product_id: int) -> HttpResponseRedirect:
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
        cart.add(product=product, quantity=cd['quantity'], override_quantity=cd['override'])

    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request: HttpRequest, product_id: int) -> HttpResponseRedirect:
    """
    Removes a product from the cart.

    Args:
        request (HttpRequest): The request object, used to access session data.
        product_id (int): The ID of the product to be removed from the cart.

    Returns:
        HttpResponseRedirect: Redirects to the cart detail page after the product has been removed.

    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request: HttpRequest) -> HttpResponseRedirect:
    """
    Renders the cart detail page.

    Args:
        request (HttpRequest): The request object, used to access session data.

    Returns:
        HttpResponse: The rendered cart detail page.

    """
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True})
    return render(request, 'cart/detail.html', {'cart': cart})

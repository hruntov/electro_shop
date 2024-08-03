from typing import Optional

from cart.forms import CartAddProductForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def product_list(request: HttpRequest, category_slug: Optional[str] = None) -> HttpResponse:
    """
    Display a list of products, optionally filtered by a given category.

    Args:
        request: HttpRequest object.
        category_slug (str, optional): Slug of the category to filter products by. Defaults to None.

    Returns:
        HttpResponse: Rendered HTML page with the list of products, along with the current category
            and all categories.

    """
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'shop/product/list.html', {'category': category,
                                                      'categories': categories,
                                                      'products': products})


def product_detail(request: HttpRequest, id: int, slug: str) -> HttpResponse:
    """
    Display the detail page for a single product.

    Args:
        request: HttpRequest object.
        id (int): The ID of the product to retrieve.
        slug (str): The slug of the product to retrieve.

    Returns:
        HttpResponse: Rendered HTML page for the product detail, including the product instance.

    """
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm
    return render(request, 'shop/product/detail.html', {'product': product,
                                                        'cart_product_form': cart_product_form})

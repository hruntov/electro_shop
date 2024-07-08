from django.shortcuts import get_object_or_404, render
from .models import Category, Product


def product_list(request, category_slug=None):
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

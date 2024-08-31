from cart.cart import Cart
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
import weasyprint

from .forms import OrderCreateForm
from .models import Order, OrderItem
from .tasks import order_created

from users.models import Profile


def order_create(request: HttpRequest) -> HttpResponse:
    """
    This view handles the creation of an order from the items in the cart.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            profile = Profile.objects.get(user=request.user)
            with transaction.atomic():
                order = form.save(commit=False)
                order.profile = profile
                order.save()
                if cart.coupon:
                    order.coupon = cart.coupon
                    order.discount = cart.coupon.discount
                order.save()
                for item in cart:
                    OrderItem.objects.create(order=order,
                                             product=item['product'],
                                             price=item['price'],
                                             quantity=item['quantity'])
                cart.clear()
                order_created.delay(order.id)
            request.session['order_id'] = order.id
            return redirect(reverse('payment:process'))
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html', {'cart': cart, 'form': form})


@staff_member_required
def admin_order_detail(request: HttpRequest, order_id: int) -> HttpResponse:
    """
    Display the details of a specific order in the admin interface.

    This view is restricted to staff members. It retrieves the order by its ID and renders the order
    detail template.

    Args:
        request (HttpRequest): The HTTP request object.
        order_id (int): The ID of the order to be displayed.

    Returns:
        HttpResponse: The HTTP response object containing the rendered order detail template.

    """
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/orders/order/detail.html', {'order': order})


@staff_member_required
def admin_order_pdf(request: HttpRequest, order_id: int) -> HttpResponse:
    """
    Generate a PDF for a specific order in the admin interface.

    Args:
        request (HttpRequest): The HTTP request object.
        order_id (int): The ID of the order for which to generate the PDF.

    Returns:
        HttpResponse: The HTTP response object containing the generated PDF.

    """
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('orders/order/pdf.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    weasyprint.HTML(string=html).write_pdf(
        response, stylesheets=[weasyprint.CSS(
            settings.STATIC_ROOT / 'css/pdf.css')])
    return response

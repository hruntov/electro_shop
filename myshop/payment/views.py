import os
import time
from decimal import Decimal

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order

from .tasks import send_invoice_email
from .wayforpay import WayForPay

wayforpay = WayForPay(key=os.getenv('SECRET_WAYFORPAY_KEY'),
                      domain_name=os.getenv('DOMAIN_NAME'))


def payment_process(request: HttpRequest) -> HttpResponse:
    """
    Handle the payment process for an order.

    This view retrieves the order from the session, creates an invoice using the WayForPay payment
    gateway, and redirects the user to the payment URL.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
    order_id = request.session.get('order_id', None)
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        cancel_url = request.build_absolute_uri(reverse('payment:canceled'))

        invoice_result = wayforpay.create_invoice(
            merchantAccount=os.getenv('WAYFORPAY_MERCHANT_LOGIN'),
            merchantAuthType='SimpleSignature',
            amount=str(order.get_total_cost()),
            currency='UAH',
            productNames=[item.product.name for item in order.items.all()],
            productPrices=[str(item.price) for item in order.items.all()],
            productCounts=[str(item.quantity) for item in order.items.all()]
        )
        order_reference = invoice_result.orderReference

        order.order_reference = order_reference
        order.save()

        if invoice_result and invoice_result.invoiceUrl:
            return redirect(invoice_result.invoiceUrl)
        else:
            return redirect(cancel_url)

    return render(request, 'payment/process.html', {'order': order})


@csrf_exempt
def payment_completed(request: HttpRequest) -> HttpResponse:
    """
    This view processes the payment completion notification from the payment gateway.

    Args:
        request (HttpRequest): The HTTP request object containing POST data from the payment
                               gateway.

    Returns:
        HttpResponse: The HTTP response object.

    """
    data = request.POST

    merchant_signature = data.get('merchantSignature')

    required_fields = [
        'merchantAccount', 'orderReference', 'amount', 'currency', 'authCode',
        'cardPan', 'transactionStatus', 'reasonCode'
    ]
    signature_data = [data[field] for field in required_fields]

    expected_signature = wayforpay.generate_signature(signature_data)

    if merchant_signature == expected_signature:
        order_reference = data.get('orderReference')
        transaction_status = data.get('transactionStatus')

        try:
            order = Order.objects.get(order_reference=order_reference)
            if transaction_status == 'Approved':
                order.paid = True
                order.save()
                send_invoice_email.delay(order.id)
            else:
                order.paid = False
        except Order.DoesNotExist:
            raise "Такого замовлення не існує"

    if order.paid is True:
        return render(request, 'payment/completed.html')
    return render(request, 'payment/canceled.html')


@csrf_exempt
def payment_canceled(request: HttpRequest) -> HttpResponse:
    """
    Handle the payment cancellation.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object.

    """
    return render(request, 'payment/canceled.html')

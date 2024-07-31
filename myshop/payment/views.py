from decimal import Decimal
import os

from django.conf import settings
from django.shortcuts import render, redirect, reverse, get_object_or_404

from orders.models import Order
from .wayforpay import WayForPay


wayforpay = WayForPay(key=os.getenv('SECRET_WAYFORPAY_KEY'),
                      domain_name=os.getenv('DOMAIN_NAME'))


def payment_process(request):
    order_id = request.session.get('order_id', None)
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('payment:completed'))
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

        if invoice_result and invoice_result.invoiceUrl:
            return redirect(invoice_result.invoiceUrl)
        else:
            return redirect(cancel_url)
    return render(request, 'payment/process.html', {'order': order})


def payment_completed(request):
    return render(request, 'payment/completed.html')


def payment_canceled(request):
    return render(request, 'payment/canceled.html')

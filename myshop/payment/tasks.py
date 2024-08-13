from io import BytesIO

import weasyprint
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from orders.models import Order


@shared_task
def send_invoice_email(order_id: int) -> None:
    """
    Sends an invoice email with a PDF attachment for the given order.

    Args:
        order_id (int): The ID of the order for which to send the invoice email.

    """
    order = Order.objects.get(id=order_id)
    subject = f'HomeBattery - Замовлення №{order.id}'
    message = 'Ваш рахунок за вашу недавню покупку.'
    email = EmailMessage(subject, message, 'admin@myshop.com', [order.email])

    html = render_to_string('orders/order/pdf.html', {'order': order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)

    email.attach(f'order_{order.id}.pdf', out.getvalue(), 'application/pdf')
    email.send()

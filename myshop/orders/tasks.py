from django.core.mail import send_mail

from celery import shared_task

from .models import Order


@shared_task
def order_created(order_id: int) -> int:
    """
    Send an email notification when an order is created.

    Args:
        order_id (int): The ID of the order that was created.

    Returns:
        int: The number of successfully delivered messages (1 if successful, 0 otherwise).

    """
    order = Order.objects.get(id=order_id)
    subject = f'Замовлення номер {order.id}'
    message = f'Дорогий {order.first_name}, \n\n' \
              f'Ми прийняли ваше замовлення.' \
              f'Номер вашого замовлення - {order.id}'
    mail_sent = send_mail(subject, message, 'admin@myshop.com', [order.email])
    return mail_sent

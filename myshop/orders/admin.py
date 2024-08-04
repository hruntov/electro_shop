import csv
from datetime import datetime

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Order, OrderItem


def order_detail(obj: Order) -> str:
    """
    Generate a link to view the details of an order in the admin interface.

    Args:
        obj (Order): The order object for which to generate the detail link.

    Returns:
        str: A safe HTML string containing the link to the order detail view.

    """
    url = reverse('orders:admin_order_detail', args=[obj.id])
    return mark_safe(f'<a href="{url}">View</a>')


def export_to_csv(modeladmin: admin.ModelAdmin, request, queryset: QuerySet) -> HttpResponse:
    """
    Export selected orders to a CSV file.

    Args:
        modeladmin (ModelAdmin): The current ModelAdmin instance.
        request (HttpRequest): The current HttpRequest instance.
        queryset (QuerySet): The queryset of selected objects to be exported.

    Returns:
        HttpResponse: An HTTP response with the CSV file attached.

    """
    opts = modeladmin.model._meta
    content_disposition = f'attachment; filename={opts.verbose_name}.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = content_disposition
    writer = csv.writer(response)
    fields = [field for field in opts.get_fields()
              if not field.many_to_many and not field.one_to_many]
    writer.writerow([field.verbose_name for field in fields])

    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)
    return response


export_to_csv.short_description = 'Експорт до CSV'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'address', 'postal_code', 'city',
                    'paid', 'created', 'updated', order_detail]
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]
    actions = [export_to_csv]

from django.http import HttpResponse, HttpRequest
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CouponApplyForm
from .models import Coupon


@require_POST
def coupon_apply(request: HttpRequest) -> HttpResponse:
    """
    Apply a coupon to the current cart session.

    Args:
        request (HttpRequest): The HTTP request object containing POST data with the coupon code.

    Returns:
        HttpResponse: A redirect response to the cart detail page.

    """
    now = timezone.now()
    form = CouponApplyForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code__iexact=code,
                                        valid_from__lte=now,
                                        valid_to__gte=now,
                                        active=True)
            request.session['coupon_id'] = coupon.id
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
    return redirect('cart:cart_detail')

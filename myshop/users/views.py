from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from orders.models import Order
from .models import Profile


@login_required
def profile(request):
    profile = Profile.objects.get(user=request.user)
    orders = Order.objects.filter(profile=profile)
    return render(request, 'users/profile.html', {'orders': orders, 'profile': profile})

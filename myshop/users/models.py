from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.TextField(blank=True, null=True, max_length=100)
    last_name = models.TextField(blank=True, null=True, max_length=100)
    email = models.EmailField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(blank=True, null=True, max_length=100)

    def __str__(self):
        return self.user.username

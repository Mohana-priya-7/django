from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Product(models.Model):
    name = models.CharField(max_length=255,unique=True)
    price = models.IntegerField()
    description = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
class ForgetPassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    """ This allows the ForgetPassword model to track which user requested a password reset. The CASCADE behavior ensures no orphaned records remain if a user account is removed."""
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user.username} - {self.otp}"
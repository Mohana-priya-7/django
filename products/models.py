from django.db import models
class Product(models.Model):
    name = models.CharField(max_length=255,unique=True)
    price = models.IntegerField()
    description = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
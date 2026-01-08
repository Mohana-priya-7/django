from django.db import models
class Product(models.Model):
    Name = models.CharField(max_length=255)
    Price = models.IntegerField()
    Description = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.Name
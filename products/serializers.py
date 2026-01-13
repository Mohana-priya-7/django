from rest_framework import serializers
from .models import Product

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class ProductSerializer(serializers.ModelSerializer):
    created_at=serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['created_at']

class DiscountSerializer(serializers.Serializer):
    discount = serializers.IntegerField(
        min_value=1,
        max_value=100, 
    )
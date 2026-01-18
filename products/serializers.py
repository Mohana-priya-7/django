from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2')
        extra_kwargs = {'email': {'required': True}}
    
    def validate(self, data):
        if data['password'] != data.get('password2'):
            raise serializers.ValidationError({'password': "Passwords must match."})
        return data
 
    def create(self, validated_data):
        validated_data.pop('password2')   # remove extra field

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

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
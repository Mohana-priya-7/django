from rest_framework import serializers
from django.contrib.auth.models import User
from products.utils import validate_strong_password
from .models import Product
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    """password – Field name that will appear in API requests/responses
serializers.CharField(...) – Specifies this is a text field that accepts string input
write_only=True – The password is only accepted during input (when creating/updating users). It's never included in API responses for security reasons—you don't want passwords leaked in responses.
Why write_only=True?When someone sends a POST request with a password, the serializer accepts it (write)
When you retrieve a user from the API, the password field won't be returned (read is blocked)
This prevents accidental exposure of sensitive password data
In context: The full line in your code also has required=True (password must be provided) and style={'input_type': 'password'} (for UI rendering as a password field).
    """
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')
        extra_kwargs = {'email': {'required': True}}    
    def validate_password(self, value):
        return validate_strong_password(value)
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)    
    def validate_new_password(self, value):
        return validate_strong_password(value)
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords do not match")
        return data

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(max_length=6, required=True)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(max_length=6, required=True)
    new_password = serializers.CharField(write_only=True)
    def validate_new_password(self, value):
        return validate_strong_password(value)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

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
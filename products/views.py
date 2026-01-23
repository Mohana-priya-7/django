from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Product
from .serializers import UserSerializer
from .serializers import ProductSerializer
from .serializers import DiscountSerializer
from .serializers import ChangePasswordSerializer
from drf_spectacular.utils import extend_schema

import random 
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import ForgetPassword
from .serializers import ForgotPasswordSerializer, VerifyOTPSerializer, ResetPasswordSerializer 

class Register(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        request=UserSerializer,
        responses={201: UserSerializer, 400: dict}
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'message': 'User registered successfully',
                    'user': UserSerializer(user).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(  
        request=ChangePasswordSerializer,
        responses={200: dict, 400: dict})
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data.get('old_password')
            new_password = serializer.validated_data.get('new_password')
            if not user.check_password(old_password):
                return Response(
                    {"error": "Old password is incorrect"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(new_password)
            user.save()
            return Response(
                {"message": "Password changed successfully"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        request=ForgotPasswordSerializer,
        responses={200: dict, 400: dict}
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User with this email does not exist"}, status=400)
            otp = str(random.randint(100000, 999999))
            ForgetPassword.objects.create(
                user=user,
                otp=otp
            )
            send_mail(
                "Password Reset OTP",
                f"Your OTP for password reset is: {otp}",
                "noreply@example.com",
                [email],
                fail_silently=False,
            )
            return Response({"message": "OTP sent to email successfully"}, status=200)
        return Response(serializer.errors, status=400)
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        request=VerifyOTPSerializer,
        responses={200: dict, 400: dict}
    )
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            try:
                user = User.objects.get(email=email)
                otp_obj = ForgetPassword.objects.filter(user=user, otp=otp, is_used=False).last()
                if not otp_obj:
                    return Response({"error": "Invalid OTP"}, status=400)
                return Response({"message": "OTP verified successfully"}, status=200)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=400)
        return Response(serializer.errors, status=400)
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        request=ResetPasswordSerializer,
        responses={200: dict, 400: dict}
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']
            try:
                user = User.objects.get(email=email)
                otp_obj = ForgetPassword.objects.filter(user=user, otp=otp, is_used=False).last()
                if not otp_obj:
                    return Response({"error": "Invalid OTP"}, status=400)
                user.set_password(new_password)
                user.save()
                otp_obj.is_used = True
                otp_obj.save()
                return Response({"message": "Password reset successfully"}, status=200)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=400)
        return Response(serializer.errors, status=400)
class ListCreate(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        responses=ProductSerializer(many=True)
    )
    def get(self, request):
        products = Product.objects.all()
        serializers = ProductSerializer(products, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
    @extend_schema(
        request=ProductSerializer,
        responses=ProductSerializer
    )
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class UpdateDelete(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        request=ProductSerializer,
        responses=ProductSerializer)
    def put(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
        responses={204: None}
    )
    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)    
class ProductTotalSales(GenericAPIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        responses={200:{
                'type': 'object',
                'properties': {
                    'Total': {'type': 'integer'}
                }
            }
        }
    )
    def get(self, request):
        t = sum(product.price for product in Product.objects.all())
        return Response({'Total' : t})
class Discount(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DiscountSerializer
    @extend_schema(
        request=DiscountSerializer)
    def put(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
           discount = serializer.validated_data["discount"]
        else:
            return Response(serializer.errors, status=400)
        product = Product.objects.get(pk=pk) 
        original = product.price
        dprice = int(original - (original * discount / 100))
        product.price = dprice
        product.save()
        return Response({
        "product": product.name,
        "original_price": original,
        "discounted_price": dprice
        }, status=status.HTTP_200_OK)
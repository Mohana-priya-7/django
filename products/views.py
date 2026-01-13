from itertools import product
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from django.contrib.auth import authenticate
from .models import Product
from .serializers import LoginSerializer
from .serializers import ProductSerializer
from .serializers import DiscountSerializer
from drf_spectacular.utils import extend_schema

class ListCreate(APIView):
    @extend_schema(
        responses=ProductSerializer(many=True)
    )
    def get(self, request):
        products=Product.objects.all()
        serializers=ProductSerializer(products, many=True)
        return Response(serializers.data,status=status.HTTP_200_OK)
    
    @extend_schema(
        request=ProductSerializer,
        responses=ProductSerializer
    )
    def post(self,request):
        serializer= ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UpdateDelete(APIView):
    @extend_schema(
        request=ProductSerializer,
        responses=ProductSerializer)
    def put(self,request,pk):
        try:
            product=Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error':'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer=ProductSerializer(product, data=request.data)
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
    
class UserLogin(APIView):
    @extend_schema(
    request=LoginSerializer,
    responses={200: dict, 401: dict}
)
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            return Response(
                {"message": "Login successful"},
                status=status.HTTP_200_OK
            )
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )
class ProductTotalSales(GenericAPIView):
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
        dprice = int(product.price - (product.price * discount / 100))
        product.price = dprice
        product.save()
        return Response({
            "product": product.name,
            "original_price": product.price,
            "discounted_price": dprice
        },status=status.HTTP_200_OK)
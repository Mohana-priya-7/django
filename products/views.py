from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer 
    @extend_schema(
            parameters=[
                OpenApiParameter(
                    name='min_price',
                    type=int,
                    location=OpenApiParameter.QUERY,
                    description='Minimum price to filter expensive products',
                )
            ]
    )
    @action(detail=False, methods=['get'])
    def expensive(self, request):
            min_price=request.query_params.get('min_price',50000)
            products = Product.objects.filter(price__gt=min_price)
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def discount(self,request,pk=None):
        product=self.get_object()
        percent=int(request.data.get('percent',0))
        product.price -= (product.price*percent//100)
        product.save()
        return Response({
        "message":f"Discount of {percent}% applied.",
        "new_price":product.price
    })

    @action(detail=True, methods=['delete'])
    def remove(self, request, pk=None):
        product = self.get_object()
        product.delete()
        return Response(
            {"message": "Product deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['patch'])
    def modify(self, request, pk=None):
        product = self.get_object()
        price = request.data.get('price')
        if price is None:
            return Response({"message": "price is required"}, status=400)
        product.price = int(price)
        product.save()
        return Response({
        "message": "Price updated successfully",
        "price": product.price
    })

def create(self, request, *args, **kwargs): 
        product, created = Product.objects.get_or_create(
            name=request.data.get("name"),
            defaults={
                "price": request.data.get("price"),
                "description": request.data.get("description"),
            }
        )
        if created:
            serializer = self.get_serializer(product)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            serializer = self.get_serializer(product)
            return Response(
                {
                    "message": "Product already exists",
                    "product": serializer.data
                },
                status=status.HTTP_200_OK
            )
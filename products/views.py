from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer 
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
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Avg, Sum, Min, Max
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Product
from .serializers import ProductSerializer
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    @swagger_auto_schema(
        method='get',
        operation_summary="Get expensive products",
        operation_description="Returns all products with price greater than some value",
        manual_parameters=[
            openapi.Parameter(
                'min_price',
                openapi.IN_QUERY,
                description="Minimum price filter (default: 50000)",
                type=openapi.TYPE_NUMBER,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="Success",
                schema=ProductSerializer(many=True)
            ),
            404: "No products found"
}
    )
    @action(detail=False, methods=['get'])
    def expensive(self, request):
        min_price = request.query_params.get('min_price', 50000)
        expensive_products = Product.objects.filter(price__gte=min_price)
        if not expensive_products.exists():
            return Response(
                {
                    "message": f"No products found above ₹{min_price}",
                    "count": 0
                },
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(expensive_products, many=True)
        return Response({
            "count": expensive_products.count(),
            "min_price_filter": float(min_price),
            "products": serializer.data
        }, status=status.HTTP_200_OK)
    @swagger_auto_schema(
        method='get',
        operation_summary="Search products by keyword",
        operation_description="Search products by name or description (case-insensitive).",
        manual_parameters=[
            openapi.Parameter(
                'q',
                openapi.IN_QUERY,
                description="Search query (required)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
        200: openapi.Response(
        description="Success",
        schema=ProductSerializer(many=True)
    ),
            400: "Search query required"
        }
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response(
                {
                    "error": "Please provide a search query using ?q=keyword",
                    "example": "/api/products/search/?q=laptop"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        serializer = self.get_serializer(products, many=True)
        return Response({
            "query": query,
            "count": products.count(),
            "results": serializer.data
        })
    @swagger_auto_schema(
        method='get',
        operation_summary="Get product statistics",
        operation_description="Seek the statistics about products.",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total_products': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'average_price': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'cheapest_product_price': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'most_expensive_product_price': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'total_inventory_value': openapi.Schema(type=openapi.TYPE_NUMBER),
                }
            )
        }
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = Product.objects.count()
        if total == 0:
            return Response({
                "message": "No products in database",
                "total_products": 0
            })
        stats = Product.objects.aggregate(
            total_count=Count('id'),
            avg_price=Avg('price'),
            min_price=Min('price'),
            max_price=Max('price'),
            total_value=Sum('price')
        )
        return Response({
            "total_products": stats['total_count'],
            "average_price": round(float(stats['avg_price']), 2),
            "cheapest_product_price": float(stats['min_price']),
            "most_expensive_product_price": float(stats['max_price']),
            "total_inventory_value": float(stats['total_value'])
        })
    @swagger_auto_schema(
        method='get',
        operation_summary="Get products in price range",
        operation_description=" Get products within a specified price range.",
        manual_parameters=[
            openapi.Parameter(
                'min',
                openapi.IN_QUERY,
                description="Minimum price",
                type=openapi.TYPE_NUMBER,
                required=True
            ),
            openapi.Parameter(
                'max',
                openapi.IN_QUERY,
                description="Maximum price",
                type=openapi.TYPE_NUMBER,
                required=True
            )
        ],
        responses={200: openapi.Response(
        description="Success",
        schema=ProductSerializer(many=True)
    ),
            400: "Invalid parameters"
        }
    )
    @action(detail=False, methods=['get'])
    def price_range(self, request):
        min_price = request.query_params.get('min')
        max_price = request.query_params.get('max')
        if not min_price or not max_price:
            return Response(
                {
                    "error": "Please provide both min and max prices",
                    "example": "/api/products/price_range/?min=50000&max=100000"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            min_price = float(min_price)
            max_price = float(max_price)
            if min_price > max_price:
                return Response(
                    {"error": "min_price cannot be greater than max_price"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {"error": "Invalid price values. Please provide numbers."},
                status=status.HTTP_400_BAD_REQUEST
            )
        products = Product.objects.filter(
            price__gte=min_price,
            price__lte=max_price
        )
        serializer = self.get_serializer(products, many=True)
        
        return Response({
            "price_range": f"₹{min_price} - ₹{max_price}",
            "count": products.count(),
            "products": serializer.data
        })
    @swagger_auto_schema(
        method='post',
        operation_summary="Apply discount to a product",
        operation_description="Apply a discount to a specific product.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['discount_percent'],
            properties={
                'discount_percent': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description='Discount percentage (1-100)',
                    example=10
                )
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'original_price': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'discount_percent': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'discount_amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'new_price': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'product': ProductSerializer()
                }
            ),
            400: "Invalid discount percentage",
            404: "Product not found"
        }
    )
    @action(detail=True, methods=['post'])
    def discount(self, request, pk=None):
        product = self.get_object()
        discount_percent = request.data.get('discount_percent')
        if not discount_percent:
            return Response(
                {
                    "error": "Please provide discount_percent in request body",
                    "example": {"discount_percent": 10}
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            discount = float(discount_percent)
            if discount <= 0 or discount > 100:
                raise ValueError("Discount must be between 1 and 100")
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        original_price = float(product.price)
        discount_amount = original_price * (discount / 100)
        new_price = original_price - discount_amount
        product.price = new_price
        product.save()
        serializer = self.get_serializer(product)
        return Response({
            "message": "Discount applied successfully",
            "original_price": round(original_price, 2),
            "discount_percent": discount,
            "discount_amount": round(discount_amount, 2),
            "new_price": round(new_price, 2),
            "product": serializer.data
        })
    @swagger_auto_schema(
        method='get',
        operation_summary="Get latest products",
        operation_description="Get the most recently added products, limited by a specified number.",
        manual_parameters=[
            openapi.Parameter(
                'limit',
                openapi.IN_QUERY,
                description="Number of products to return (default: 5)",
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
        200: openapi.Response(
        description="Success",
        schema=ProductSerializer(many=True)
    ),
        404: "No products found"
}
    )
    @action(detail=False, methods=['get'])
    def latest(self, request):
        limit = int(request.query_params.get('limit', 5))
        if limit < 1:
            limit = 5
        if limit > 100:
            limit = 100
        latest_products = Product.objects.order_by('-created_at')[:limit]
        serializer = self.get_serializer(latest_products, many=True)
        return Response({
            "count": len(latest_products),
            "limit": limit,
            "products": serializer.data
        })
    @swagger_auto_schema(
        method='post',
        operation_summary="Bulk create products",
        operation_description="Bulkly create multiple products in a single request.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['products'],
            properties={
                'products': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'description': openapi.Schema(type=openapi.TYPE_STRING),
                            'price': openapi.Schema(type=openapi.TYPE_NUMBER)
                        }
                    )
                )
            }
        ),
        responses={
    200: openapi.Response(
        description="Success",
        schema=ProductSerializer(many=True)
    ),
            400: "Invalid data"
        }
    )
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        products_data = request.data.get('products', [])
        if not products_data or not isinstance(products_data, list):
            return Response(
                {
                    "error": "Please provide an array of products",
                    "example": {
                        "products": [
                            {"name": "Product 1", "description": "Desc", "price": 1000}
                        ]
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        created_products = []
        errors = []
        for i, product_data in enumerate(products_data):
            serializer = self.get_serializer(data=product_data)
            if serializer.is_valid():
                product = serializer.save()
                created_products.append(serializer.data)
            else:
                errors.append({
                    "index": i,
                    "data": product_data,
                    "errors": serializer.errors
                })
        return Response({
            "message": f"Successfully created {len(created_products)} products",
            "created_count": len(created_products),
            "error_count": len(errors),
            "created_products": created_products,
            "errors": errors
        }, status=status.HTTP_201_CREATED if created_products else status.HTTP_400_BAD_REQUEST) @swagger_auto_schema(
        method='get',
        operation_summary="Get affordable products",
        operation_description="Get products cheaper than a specified maximum price, ordered by price ascending.",
        responses={200: ProductSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def cheap(self, request):
        cheap_products = Product.objects.filter(
            price__lt=30000
        ).order_by('price') 
        serializer = self.get_serializer(cheap_products, many=True)
        return Response({
            "max_price": 30000,
            "count": cheap_products.count(),
            "products": serializer.data
        })
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from products.views import ProductViewSet
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
schema_view = get_schema_view(
    openapi.Info(
        title="Product Management API",
        default_version='v1.0',
        description="API for managing products including creation, retrieval, updating, and deletion.",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(
            name="Your Name",
            email="your-email@company.com"
        ),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('swagger/', 
         schema_view.with_ui('swagger', cache_timeout=0), 
         name='schema-swagger-ui'),
    path('redoc/', 
         schema_view.with_ui('redoc', cache_timeout=0), 
         name='schema-redoc'),
    path('swagger.json', 
         schema_view.without_ui(cache_timeout=0), 
         name='schema-json'),
    path('swagger.yaml', 
         schema_view.without_ui(cache_timeout=0), 
         name='schema-yaml'),
]
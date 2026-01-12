from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from products.views import ProductViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView 
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
     # drf-spectacular schema & swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
]
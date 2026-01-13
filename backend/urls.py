from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
urlpatterns = [
    path('admin/', admin.site.urls),
    # OpenAPI schema generation endpoint
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),    
    path('', include('products.urls')),
]
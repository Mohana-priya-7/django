from django.urls import path
from .views import Register,ListCreate, UpdateDelete, ProductTotalSales, Discount
urlpatterns = [
    path('register/', Register.as_view(), name='register'),
    path('products/', ListCreate.as_view(), name='products'),
    path('products/<int:pk>/', UpdateDelete.as_view(), name='product-detail'),
    path('total-sales/', ProductTotalSales.as_view(), name='total-sales'),
    path('discount/<int:pk>/', Discount.as_view(), name='discount'),
]
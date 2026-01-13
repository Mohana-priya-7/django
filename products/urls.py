from django.urls import path
from .views import ListCreate, ProductTotalSales,UpdateDelete,UserLogin, ProductTotalSales,Discount
urlpatterns = [
    path('products/', ListCreate.as_view(), name='products'),
    path('products/<int:pk>/',UpdateDelete.as_view(), name='product-detail'),
    path('login/', UserLogin.as_view(), name='user-login'),
    path('total-sales/',ProductTotalSales.as_view(), name='total-sales'),
    path('discount/<int:pk>/',Discount.as_view(), name='discount'),
]
from django.urls import path
from .views import ChangePasswordView, Register,ListCreate, UpdateDelete, ProductTotalSales, Discount
from .views import ForgotPasswordView, VerifyOTPView, ResetPasswordView
urlpatterns = [
    path('register/', Register.as_view(), name='register'),
    path('products/', ListCreate.as_view(), name='products'),
    path('products/<int:pk>/', UpdateDelete.as_view(), name='product-detail'),
    path('total-sales/', ProductTotalSales.as_view(), name='total-sales'),
    path('discount/<int:pk>/', Discount.as_view(), name='discount'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('forgot-password/', ForgotPasswordView.as_view()),
    path('verify-otp/', VerifyOTPView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),
]
from django.urls import path
from .views import (
    ProductListAPIView,
    ProductDetailAPIView,
    ProductVariantListAPIView,
    FilterOptionsAPIView
)

urlpatterns = [
    path('', ProductListAPIView.as_view(), name='product-list'),
    path('filters/', FilterOptionsAPIView.as_view(), name='filter-options'),
    path('<slug:slug>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('<slug:product_slug>/variants/', ProductVariantListAPIView.as_view(), name='product-variants'),
]
from django.urls import path
from .views import (
    CategoryListAPIView,
    AllCategoriesAPIView,
    CategoryDetailAPIView,
    CategoryProductsAPIView,
    CategoryCreateAPIView,
    CategoryUpdateAPIView,
    CategoryDeleteAPIView
)

urlpatterns = [
    # Public endpoints
    path('', CategoryListAPIView.as_view(), name='category-list'),
    path('all/', AllCategoriesAPIView.as_view(), name='all-categories'),
    path('<slug:slug>/', CategoryDetailAPIView.as_view(), name='category-detail'),
    path('<slug:slug>/products/', CategoryProductsAPIView.as_view(), name='category-products'),
    
    # Admin endpoints (will add permission later)
    path('create/', CategoryCreateAPIView.as_view(), name='category-create'),
    path('update/<slug:slug>/', CategoryUpdateAPIView.as_view(), name='category-update'),
    path('delete/<slug:slug>/', CategoryDeleteAPIView.as_view(), name='category-delete'),
]
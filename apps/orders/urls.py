from django.urls import path
from .views import (
    OrderCreateAPIView,
    OrderDetailAPIView,
    OrderListByEmailAPIView,
    OrderStatusUpdateAPIView
)

urlpatterns = [
    path('create/', OrderCreateAPIView.as_view(), name='order-create'),
    path('<str:order_id>/', OrderDetailAPIView.as_view(), name='order-detail'),
    path('lookup/email/', OrderListByEmailAPIView.as_view(), name='order-by-email'),
    path('<str:order_id>/status/', OrderStatusUpdateAPIView.as_view(), name='order-status-update'),
]
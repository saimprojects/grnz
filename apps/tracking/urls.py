from django.urls import path
from .views import (
    TrackOrderByIDAPIView,
    TrackOrderByPhoneAPIView,
    AddTrackingUpdateAPIView,
    UpdateCourierInfoAPIView,
    TrackingTimelineAPIView
)

urlpatterns = [
    # Public tracking endpoints
    path('<str:order_id>/', TrackOrderByIDAPIView.as_view(), name='track-by-id'),
    path('timeline/<str:order_id>/', TrackingTimelineAPIView.as_view(), name='tracking-timeline'),
    path('lookup/phone/', TrackOrderByPhoneAPIView.as_view(), name='track-by-phone'),
    
    # Admin endpoints
    path('<str:order_id>/add-update/', AddTrackingUpdateAPIView.as_view(), name='add-tracking-update'),
    path('<str:order_id>/update-courier/', UpdateCourierInfoAPIView.as_view(), name='update-courier-info'),
]
from django.urls import path
from .views import (
    ContactCreateAPIView,
    ContactListAPIView,
    ContactDetailAPIView,
    AdminContactResponseAPIView,
    ContactResolveAPIView,
    MyContactsAPIView,
    ContactStatsAPIView,
    NewsletterSubscribeAPIView,
    NewsletterUnsubscribeAPIView
)

urlpatterns = [
    # Public endpoints
    path('create/', ContactCreateAPIView.as_view(), name='contact-create'),
    path('my-contacts/', MyContactsAPIView.as_view(), name='my-contacts'),
    
    # Newsletter endpoints
    path('newsletter/subscribe/', NewsletterSubscribeAPIView.as_view(), name='newsletter-subscribe'),
    path('newsletter/unsubscribe/', NewsletterUnsubscribeAPIView.as_view(), name='newsletter-unsubscribe'),
    
    # Admin endpoints
    path('admin/all/', ContactListAPIView.as_view(), name='admin-contacts'),
    path('admin/<int:id>/', ContactDetailAPIView.as_view(), name='admin-contact-detail'),
    path('admin/<int:contact_id>/respond/', AdminContactResponseAPIView.as_view(), name='admin-contact-response'),
    path('admin/<int:contact_id>/resolve/', ContactResolveAPIView.as_view(), name='admin-contact-resolve'),
    path('admin/stats/', ContactStatsAPIView.as_view(), name='admin-contact-stats'),
]
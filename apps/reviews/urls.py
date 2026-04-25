from django.urls import path
from .views import (
    ReviewListAPIView,
    AllReviewsAPIView,
    ReviewCreateAPIView,
    ReviewDetailAPIView,
    ProductRatingSummaryAPIView,
    ReviewVoteAPIView,
    AdminReviewResponseAPIView
)

urlpatterns = [
    # Public endpoints
    path('product/<int:product_id>/', ReviewListAPIView.as_view(), name='product-reviews'),
    path('product/<int:product_id>/summary/', ProductRatingSummaryAPIView.as_view(), name='product-rating-summary'),
    path('all/', AllReviewsAPIView.as_view(), name='all-reviews'),
    path('create/', ReviewCreateAPIView.as_view(), name='review-create'),
    path('<int:id>/', ReviewDetailAPIView.as_view(), name='review-detail'),
    path('<int:review_id>/vote/', ReviewVoteAPIView.as_view(), name='review-vote'),
    
    # Admin endpoints
    path('<int:review_id>/respond/', AdminReviewResponseAPIView.as_view(), name='admin-review-response'),
]
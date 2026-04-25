from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404
from .models import Review, ReviewVote
from .serializers import ReviewSerializer, ReviewCreateSerializer, ReviewVoteSerializer, ProductRatingSummarySerializer
from apps.products.models import Product

class ReviewListAPIView(generics.ListAPIView):
    """Get all approved reviews for a product"""
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return Review.objects.filter(
            product_id=product_id,
            is_approved=True
        )

class AllReviewsAPIView(generics.ListAPIView):
    """Get all approved reviews (for homepage features)"""
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        queryset = Review.objects.filter(is_approved=True)
        
        # Filter by rating
        rating = self.request.query_params.get('rating')
        if rating:
            queryset = queryset.filter(rating=rating)
        
        # Featured reviews only
        featured = self.request.query_params.get('featured')
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset.order_by('-created_at')

class ReviewCreateAPIView(generics.CreateAPIView):
    """Create a new review (no auth required)"""
    serializer_class = ReviewCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if user already reviewed
        product = serializer.validated_data.get('product')
        email = serializer.validated_data.get('customer_email')
        
        if Review.objects.filter(product=product, customer_email=email).exists():
            return Response({
                'success': False,
                'error': 'You have already reviewed this product'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        
        return Response({
            'success': True,
            'message': 'Review submitted successfully! It will appear after admin approval.',
            'review': serializer.data
        }, status=status.HTTP_201_CREATED)

class ReviewDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a review"""
    queryset = Review.objects.filter(is_approved=True)
    serializer_class = ReviewSerializer
    lookup_field = 'id'

class ProductRatingSummaryAPIView(APIView):
    """Get rating summary for a product"""
    
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Get all approved reviews for this product
        reviews = Review.objects.filter(product=product, is_approved=True)
        
        # Calculate average rating
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        
        # Calculate rating distribution (how many 1-star, 2-star, etc.)
        distribution = {}
        percentages = {}
        
        for i in range(1, 6):
            count = reviews.filter(rating=i).count()
            distribution[str(i)] = count
            if reviews.count() > 0:
                percentages[str(i)] = round((count / reviews.count()) * 100, 1)
            else:
                percentages[str(i)] = 0
        
        # Get recent reviews
        recent_reviews = reviews.order_by('-created_at')[:5]
        
        return Response({
            'product_id': product.id,
            'product_name': product.name,
            'average_rating': round(avg_rating, 1),
            'total_reviews': reviews.count(),
            'rating_distribution': distribution,
            'rating_percentages': percentages,
            'recent_reviews': ReviewSerializer(recent_reviews, many=True).data
        })

class ReviewVoteAPIView(APIView):
    """Vote on a review (helpful/not helpful)"""
    
    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id, is_approved=True)
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        serializer = ReviewVoteSerializer(data=request.data)
        if serializer.is_valid():
            is_helpful = serializer.validated_data['is_helpful']
            
            # Check if already voted
            existing_vote = ReviewVote.objects.filter(
                review=review,
                ip_address=ip_address
            ).first()
            
            if existing_vote:
                # Update existing vote
                if existing_vote.is_helpful != is_helpful:
                    # Change vote
                    if is_helpful:
                        review.helpful_count += 1
                        review.not_helpful_count -= 1
                    else:
                        review.helpful_count -= 1
                        review.not_helpful_count += 1
                    
                    existing_vote.is_helpful = is_helpful
                    existing_vote.save()
                    review.save()
                    
                    return Response({
                        'success': True,
                        'message': 'Vote updated',
                        'helpful_count': review.helpful_count,
                        'not_helpful_count': review.not_helpful_count
                    })
                else:
                    return Response({
                        'success': False,
                        'message': 'You have already voted this way'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Create new vote
                ReviewVote.objects.create(
                    review=review,
                    ip_address=ip_address,
                    is_helpful=is_helpful
                )
                
                if is_helpful:
                    review.helpful_count += 1
                else:
                    review.not_helpful_count += 1
                review.save()
                
                return Response({
                    'success': True,
                    'message': 'Vote recorded',
                    'helpful_count': review.helpful_count,
                    'not_helpful_count': review.not_helpful_count
                })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminReviewResponseAPIView(APIView):
    """Allow admin to respond to reviews"""
    
    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        admin_response = request.data.get('admin_response')
        
        if not admin_response:
            return Response({
                'success': False,
                'error': 'Response text is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from django.utils import timezone
        review.admin_response = admin_response
        review.admin_response_date = timezone.now()
        review.save()
        
        return Response({
            'success': True,
            'message': 'Response added to review',
            'admin_response': review.admin_response,
            'admin_response_date': review.admin_response_date
        })
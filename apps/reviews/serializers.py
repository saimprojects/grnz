from rest_framework import serializers
from .models import Review, ReviewVote

class ReviewSerializer(serializers.ModelSerializer):
    rating_percentage = serializers.ReadOnlyField()
    is_verified_purchase = serializers.ReadOnlyField()
    admin_response_date_formatted = serializers.SerializerMethodField()
    created_at_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'product', 'customer_name', 'customer_email',
            'rating', 'rating_percentage', 'title', 'comment',
            'image', 'is_approved', 'is_featured', 'is_verified_purchase',
            'admin_response', 'admin_response_date', 'admin_response_date_formatted',
            'helpful_count', 'not_helpful_count',
            'created_at', 'created_at_formatted', 'updated_at'
        ]
        read_only_fields = ['is_approved', 'is_featured', 'helpful_count', 'not_helpful_count']
    
    def get_admin_response_date_formatted(self, obj):
        if obj.admin_response_date:
            return obj.admin_response_date.strftime("%B %d, %Y")
        return None
    
    def get_created_at_formatted(self, obj):
        return obj.created_at.strftime("%B %d, %Y")
    
    def validate(self, data):
        # Check if user already reviewed this product
        if not self.instance:  # Only for create
            if Review.objects.filter(
                product=data.get('product'),
                customer_email=data.get('customer_email')
            ).exists():
                raise serializers.ValidationError("You have already reviewed this product")
        return data

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'product', 'customer_name', 'customer_email',
            'rating', 'title', 'comment', 'image'
        ]
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

class ReviewVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewVote
        fields = ['is_helpful']

class ProductRatingSummarySerializer(serializers.Serializer):
    """Summary of ratings for a product"""
    average_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
    rating_distribution = serializers.DictField()
    rating_percentages = serializers.DictField()
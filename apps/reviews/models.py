from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.products.models import Product

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    
    # Customer information (no auth required)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    
    # Review content
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 to 5 stars'
    )
    title = models.CharField(max_length=200, blank=True, help_text='Review title (optional)')
    comment = models.TextField()
    
    # Images (optional)
    image = models.ImageField(upload_to='reviews/', null=True, blank=True)
    
    # Status
    is_approved = models.BooleanField(default=False, help_text='Approve review to show on website')
    is_featured = models.BooleanField(default=False, help_text='Feature this review on homepage')
    
    # Admin response
    admin_response = models.TextField(blank=True, null=True, help_text='Admin can respond to review')
    admin_response_date = models.DateTimeField(blank=True, null=True)
    
    # Helpful votes
    helpful_count = models.IntegerField(default=0)
    not_helpful_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ['product', 'customer_email']  # One review per product per email
    
    def __str__(self):
        return f"{self.product.name} - {self.rating}★ by {self.customer_name}"
    
    @property
    def rating_percentage(self):
        """Return rating as percentage (for star display)"""
        return (self.rating / 5) * 100
    
    @property
    def is_verified_purchase(self):
        """Check if customer actually purchased this product"""
        from apps.orders.models import OrderItem, GhostOrder
        try:
            # Check if there's a delivered order with this product for this email
            has_purchased = OrderItem.objects.filter(
                product_name=self.product.name,
                order__customer_email=self.customer_email,
                order__status='delivered'
            ).exists()
            return has_purchased
        except:
            return False

class ReviewVote(models.Model):
    """Track who voted helpful/not helpful on reviews"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='votes')
    ip_address = models.GenericIPAddressField()
    is_helpful = models.BooleanField()
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['review', 'ip_address']
        verbose_name = 'Review Vote'
        verbose_name_plural = 'Review Votes'
    
    def __str__(self):
        return f"{self.review.id} - {'Helpful' if self.is_helpful else 'Not Helpful'}"
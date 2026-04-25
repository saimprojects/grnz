from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Review, ReviewVote

class ReviewVoteInline(admin.TabularInline):
    model = ReviewVote
    extra = 0
    readonly_fields = ['ip_address', 'is_helpful', 'voted_at']
    can_delete = False
    max_num = 0

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product_link', 'customer_name', 'rating_stars', 'title_preview', 'is_approved', 'is_featured', 'helpful_count', 'created_at']
    list_display_links = ['customer_name', 'product_link']
    list_editable = ['is_approved', 'is_featured']
    search_fields = ['customer_name', 'customer_email', 'comment', 'product__name']
    list_filter = ['rating', 'is_approved', 'is_featured', 'created_at', 'product__category']
    readonly_fields = ['helpful_count', 'not_helpful_count', 'created_at', 'updated_at', 'rating_stars_display', 'verified_badge']
    
    inlines = [ReviewVoteInline]
    
    fieldsets = (
        ('Product & Customer', {
            'fields': ('product', 'customer_name', 'customer_email', 'verified_badge')
        }),
        ('Review Content', {
            'fields': ('rating', 'rating_stars_display', 'title', 'comment')
        }),
        ('Media', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        ('Status & Engagement', {
            'fields': ('is_approved', 'is_featured', 'helpful_count', 'not_helpful_count')
        }),
        ('Admin Response', {
            'fields': ('admin_response', 'admin_response_date'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def product_link(self, obj):
        url = reverse('admin:products_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'
    
    def title_preview(self, obj):
        if obj.title:
            return obj.title[:50]
        return format_html('<span style="color: gray;">No title</span>')
    title_preview.short_description = 'Title'
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #ffc107; font-size: 14px;">{}</span>', stars)
    rating_stars.short_description = 'Rating'
    
    def rating_stars_display(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #ffc107; font-size: 18px;">{}</span> ({}/5)', stars, obj.rating)
    rating_stars_display.short_description = 'Rating Stars'
    
    def verified_badge(self, obj):
        if obj.is_verified_purchase:
            return format_html('<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 4px;">✓ Verified Purchase</span>')
        return format_html('<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 4px;">Unverified</span>')
    verified_badge.short_description = 'Verification Status'
    
    actions = ['approve_reviews', 'unapprove_reviews', 'feature_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} reviews approved.")
    approve_reviews.short_description = "Approve selected reviews"
    
    def unapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} reviews unapproved.")
    unapprove_reviews.short_description = "Unapprove selected reviews"
    
    def feature_reviews(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"{queryset.count()} reviews featured.")
    feature_reviews.short_description = "Feature selected reviews"
    
    def save_model(self, request, obj, form, change):
        if obj.admin_response and not obj.admin_response_date:
            from django.utils import timezone
            obj.admin_response_date = timezone.now()
        super().save_model(request, obj, form, change)

class ReviewVoteAdmin(admin.ModelAdmin):
    list_display = ['review', 'ip_address', 'is_helpful', 'voted_at']
    list_filter = ['is_helpful', 'voted_at']
    search_fields = ['review__customer_name', 'review__product__name', 'ip_address']
    readonly_fields = ['review', 'ip_address', 'is_helpful', 'voted_at']

admin.site.register(Review, ReviewAdmin)
admin.site.register(ReviewVote, ReviewVoteAdmin)
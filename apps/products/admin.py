from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Product, ProductVariant, ProductImage

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['size', 'color', 'sku', 'price', 'stock_quantity', 'image', 'is_active']
    
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']

class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'base_price', 'discounted_price', 'delivery_charges', 'final_price_display', 'discount_percentage_display', 'is_active', 'is_featured', 'created_at']
    list_display_links = ['id', 'name']
    list_editable = ['is_active', 'is_featured']
    search_fields = ['name', 'slug', 'category__name']
    list_filter = ['category', 'is_active', 'is_featured', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'final_price_display', 'discount_percentage_display', 'delivery_status_display']
    
    inlines = [ProductVariantInline, ProductImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        ('Pricing', {
            'fields': ('base_price', 'discounted_price', 'final_price_display', 'discount_percentage_display')
        }),
        ('Shipping', {
            'fields': ('delivery_charges', 'delivery_status_display'),
            'classes': ('wide',),
            'description': 'Set delivery charges for this product. Leave 0 for Free Shipping.'
        }),
        ('Media', {
            'fields': ('thumbnail',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def final_price_display(self, obj):
        return f"Rs. {obj.final_price}"
    final_price_display.short_description = 'Final Price'
    
    def discount_percentage_display(self, obj):
        if obj.discount_percentage:
            return format_html('<span style="color: green;">{}% OFF</span>', obj.discount_percentage)
        return mark_safe('-')
    discount_percentage_display.short_description = 'Discount'
    
    def delivery_status_display(self, obj):
        """Display delivery status with proper formatting"""
        if obj.delivery_charges == 0 or obj.delivery_charges is None:
            return mark_safe('<span style="color: green; font-weight: bold;">✓ Free Shipping</span>')
        return mark_safe(f'<span style="color: orange;">Rs. {obj.delivery_charges}</span>')
    delivery_status_display.short_description = 'Delivery Status'

class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'size', 'color', 'sku', 'price', 'stock_quantity', 'in_stock_display', 'is_active']
    list_editable = ['price', 'stock_quantity', 'is_active']
    search_fields = ['sku', 'product__name']
    list_filter = ['size', 'color', 'is_active', 'product__category']
    
    def in_stock_display(self, obj):
        if obj.in_stock:
            return mark_safe('<span style="color: green;">✓ In Stock</span>')
        return mark_safe('<span style="color: red;">✗ Out of Stock</span>')
    in_stock_display.short_description = 'Stock Status'

class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'image_preview', 'is_primary', 'order']
    list_editable = ['is_primary', 'order']
    list_filter = ['product', 'is_primary']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 4px; object-fit: cover;" />', obj.image.url)
        return mark_safe('<span style="color: gray;">No Image</span>')
    image_preview.short_description = 'Preview'

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
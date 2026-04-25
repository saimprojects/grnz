from django.contrib import admin
from django.utils.html import format_html
from .models import GhostOrder, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'variant_details', 'quantity', 'unit_price', 'total_price']
    can_delete = False
    max_num = 0

class GhostOrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'customer_name', 'customer_phone', 'city', 'subtotal', 'delivery_charges', 'total_amount', 'status', 'payment_status', 'created_at']
    list_display_links = ['order_id', 'customer_name']
    list_editable = ['status', 'payment_status']
    search_fields = ['order_id', 'customer_name', 'customer_email', 'customer_phone', 'city']
    list_filter = ['status', 'payment_status', 'province', 'city', 'created_at']
    readonly_fields = ['order_id', 'subtotal', 'delivery_charges', 'total_amount', 'created_at', 'updated_at', 'full_address_display']
    
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'status', 'payment_status', 'payment_method')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Address Details', {
            'fields': ('province', 'city', 'main_address', 'street_number', 'house_number', 'landmark', 'full_address_display'),
            'classes': ('wide',)
        }),
        ('Order Summary', {
            'fields': ('subtotal', 'delivery_charges', 'total_amount')
        }),
        ('Notes', {
            'fields': ('notes', 'admin_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def full_address_display(self, obj):
        return format_html('<div style="background: #f8f9fa; padding: 10px; border-radius: 5px;">{}</div>', obj.full_address)
    full_address_display.short_description = 'Complete Address'
    
    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f"{updated} orders marked as confirmed.")
    mark_as_confirmed.short_description = "Mark selected orders as Confirmed"
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f"{updated} orders marked as shipped.")
    mark_as_shipped.short_description = "Mark selected orders as Shipped"
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered', payment_status='paid')
        self.message_user(request, f"{updated} orders marked as delivered.")
    mark_as_delivered.short_description = "Mark selected orders as Delivered"
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f"{updated} orders marked as cancelled.")
    mark_as_cancelled.short_description = "Mark selected orders as Cancelled"

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'variant_details', 'quantity', 'unit_price', 'total_price']
    search_fields = ['order__order_id', 'product_name']
    list_filter = ['order__status', 'order__created_at']
    readonly_fields = ['order', 'product_name', 'variant_details', 'quantity', 'unit_price', 'total_price']

admin.site.register(GhostOrder, GhostOrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
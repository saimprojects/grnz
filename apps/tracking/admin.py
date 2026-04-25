from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import OrderTracking

class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ['order_link', 'order_status', 'courier_name', 'tracking_number', 'estimated_delivery', 'last_updated']
    list_filter = ['order__status', 'courier_name', 'estimated_delivery']
    search_fields = ['order__order_id', 'tracking_number', 'order__customer_name', 'order__customer_phone']
    readonly_fields = ['status_timeline_display', 'last_updated', 'created_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order',)
        }),
        ('Courier Information', {
            'fields': ('courier_name', 'tracking_number', 'estimated_delivery')
        }),
        ('Tracking Updates', {
            'fields': ('current_location', 'status_timeline_display'),
            'classes': ('wide',)
        }),
        ('Add New Update', {
            'fields': ('add_status', 'add_note', 'add_location'),
            'description': 'Add a new status update for this order'
        }),
        ('Timestamps', {
            'fields': ('last_updated', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def order_link(self, obj):
        url = reverse('admin:orders_ghostorder_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_id)
    order_link.short_description = 'Order ID'
    
    def order_status(self, obj):
        status_colors = {
            'pending': 'gray',
            'confirmed': 'blue',
            'processing': 'orange',
            'shipped': 'purple',
            'out_for_delivery': 'gold',
            'delivered': 'green',
            'cancelled': 'red',
        }
        color = status_colors.get(obj.order.status, 'black')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', 
                          color, obj.order.status.upper())
    order_status.short_description = 'Order Status'
    
    def status_timeline_display(self, obj):
        if not obj.status_updates:
            return format_html('<p style="color: gray;">No updates yet</p>')
        
        html = '<div style="max-height: 400px; overflow-y: auto;">'
        html += '<table style="width: 100%; border-collapse: collapse;">'
        
        for update in reversed(obj.status_updates):  # Show latest first
            status_color = {
                'pending': '#6c757d',
                'confirmed': '#007bff',
                'processing': '#fd7e14',
                'shipped': '#6f42c1',
                'out_for_delivery': '#ffc107',
                'delivered': '#28a745',
                'cancelled': '#dc3545',
            }.get(update.get('status'), '#6c757d')
            
            html += f'''
            <tr style="border-bottom: 1px solid #dee2e6;">
                <td style="padding: 10px; width: 180px;">
                    <span style="background: {status_color}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px;">
                        {update.get('status', '').upper()}
                    </span>
                </td>
                <td style="padding: 10px; width: 180px; color: #6c757d; font-size: 12px;">
                    {update.get('timestamp', '')}
                </td>
                <td style="padding: 10px;">
                    <strong>📍 {update.get('location', '')}</strong><br>
                    <span style="color: #495057;">📝 {update.get('note', 'No notes')}</span>
                </td>
            </tr>
            '''
        
        html += '</table></div>'
        return format_html(html)
    status_timeline_display.short_description = 'Status Timeline'
    
    def add_status(self, obj):
        """This field appears in admin but is handled via custom JS"""
        return format_html('''
        <select id="id_add_status" style="width: 200px;">
            <option value="">-- Select Status --</option>
            <option value="confirmed">Confirmed</option>
            <option value="processing">Processing</option>
            <option value="shipped">Shipped</option>
            <option value="out_for_delivery">Out for Delivery</option>
            <option value="delivered">Delivered</option>
            <option value="cancelled">Cancelled</option>
        </select>
        ''')
    add_status.short_description = 'New Status'
    
    def add_note(self, obj):
        return format_html('<textarea id="id_add_note" rows="2" style="width: 100%;" placeholder="Admin notes about this update..."></textarea>')
    add_note.short_description = 'Update Note'
    
    def add_location(self, obj):
        return format_html('<input type="text" id="id_add_location" style="width: 100%;" placeholder="e.g., Lahore Sortation Center">')
    add_location.short_description = 'Current Location'
    
    class Media:
        js = ('admin/js/tracking_admin.js',)
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # Check if new status was added via POST
        if 'add_status' in request.POST and request.POST['add_status']:
            new_status = request.POST.get('add_status')
            note = request.POST.get('add_note', '')
            location = request.POST.get('add_location', '')
            
            # Add the status update
            update = {
                'status': new_status,
                'timestamp': models.DateTimeField(auto_now_add=True).__str__(),
                'note': note,
                'location': location
            }
            
            if not obj.status_updates:
                obj.status_updates = []
            
            obj.status_updates.append(update)
            obj.order.status = new_status
            obj.order.save()
            
            if location:
                obj.current_location = location
            
            obj.save()

admin.site.register(OrderTracking, OrderTrackingAdmin)
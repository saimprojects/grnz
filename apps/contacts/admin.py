from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from .models import Contact, NewsletterSubscriber

class ContactAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_preview', 'email', 'subject_type', 'subject_preview', 'priority', 'priority_badge', 'response_status_badge', 'is_resolved', 'created_at']
    list_display_links = ['id', 'name_preview']
    list_editable = ['priority', 'is_resolved']
    search_fields = ['name', 'email', 'subject', 'message', 'phone']
    list_filter = ['subject_type', 'priority', 'is_resolved', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'response_status_display', 'attachment_link', 'priority_badge', 'response_status_badge']
    
    fieldsets = (
        ('Sender Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message Details', {
            'fields': ('subject_type', 'subject', 'message', 'attachment', 'attachment_link')
        }),
        ('Status & Priority', {
            'fields': ('priority', 'is_resolved', 'resolved_at', 'response_status_display')
        }),
        ('Admin Response', {
            'fields': ('admin_response', 'admin_response_at', 'responded_by'),
            'classes': ('wide',)
        }),
        ('Internal Notes', {
            'fields': ('internal_notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def name_preview(self, obj):
        return obj.name[:30] if obj.name else '-'
    name_preview.short_description = 'Name'
    
    def subject_preview(self, obj):
        return obj.subject[:50] if obj.subject else '-'
    subject_preview.short_description = 'Subject'
    
    def priority_badge(self, obj):
        colors = {
            'low': '#6c757d',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'urgent': '#dc3545',
        }
        color = colors.get(obj.priority, '#6c757d')
        # Using mark_safe for static HTML with proper formatting
        return mark_safe(f'<span style="background: {color}; color: white; padding: 3px 8px; border-radius: 4px;">{obj.priority.upper()}</span>')
    priority_badge.short_description = 'Priority'
    
    def response_status_badge(self, obj):
        if obj.admin_response:
            return mark_safe('<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 4px;">✓ Responded</span>')
        elif obj.is_resolved:
            return mark_safe('<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 4px;">Resolved</span>')
        else:
            return mark_safe('<span style="background: #ffc107; color: black; padding: 3px 8px; border-radius: 4px;">⏳ Pending</span>')
    response_status_badge.short_description = 'Status'
    
    def response_status_display(self, obj):
        if obj.admin_response:
            response_time = obj.admin_response_at.strftime("%Y-%m-%d %H:%M") if obj.admin_response_at else 'N/A'
            return mark_safe(f'<span style="color: green;">✓ Response sent on {response_time}</span>')
        elif obj.is_resolved:
            return mark_safe('<span style="color: gray;">Resolved without response</span>')
        else:
            return mark_safe('<span style="color: orange;">Awaiting response</span>')
    response_status_display.short_description = 'Response Status'
    
    def attachment_link(self, obj):
        if obj.attachment:
            return mark_safe(f'<a href="{obj.attachment.url}" target="_blank">📎 Download Attachment</a>')
        return '-'
    attachment_link.short_description = 'Attachment'
    
    actions = ['mark_as_resolved', 'mark_as_pending', 'mark_as_urgent', 'send_bulk_response']
    
    def mark_as_resolved(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_resolved=True, resolved_at=timezone.now())
        self.message_user(request, f"{queryset.count()} contacts marked as resolved.")
    mark_as_resolved.short_description = "Mark selected as Resolved"
    
    def mark_as_pending(self, request, queryset):
        queryset.update(is_resolved=False, resolved_at=None)
        self.message_user(request, f"{queryset.count()} contacts marked as pending.")
    mark_as_pending.short_description = "Mark selected as Pending"
    
    def mark_as_urgent(self, request, queryset):
        queryset.update(priority='urgent')
        self.message_user(request, f"{queryset.count()} contacts marked as urgent.")
    mark_as_urgent.short_description = "Mark selected as Urgent"
    
    def send_bulk_response(self, request, queryset):
        # This would trigger email sending in production
        self.message_user(request, f"Bulk response feature - would send to {queryset.count()} contacts")
    send_bulk_response.short_description = "Send bulk email response"
    
    def save_model(self, request, obj, form, change):
        # If admin response is added/updated
        if obj.admin_response and not obj.admin_response_at:
            from django.utils import timezone
            obj.admin_response_at = timezone.now()
            obj.responded_by = request.user.username
            obj.is_resolved = True
            obj.resolved_at = timezone.now()
        super().save_model(request, obj, form, change)

class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at']
    list_editable = ['is_active']
    search_fields = ['email']
    list_filter = ['is_active', 'subscribed_at']
    actions = ['export_as_csv']
    
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="subscribers.csv"'
        writer = csv.writer(response)
        writer.writerow(['Email', 'Subscribed Date', 'Status'])
        for subscriber in queryset:
            writer.writerow([subscriber.email, subscriber.subscribed_at, 'Active' if subscriber.is_active else 'Inactive'])
        return response
    export_as_csv.short_description = "Export selected to CSV"

admin.site.register(Contact, ContactAdmin)
admin.site.register(NewsletterSubscriber, NewsletterSubscriberAdmin)
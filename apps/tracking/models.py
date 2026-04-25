from django.db import models
from apps.orders.models import GhostOrder

class OrderTracking(models.Model):
    order = models.OneToOneField(GhostOrder, on_delete=models.CASCADE, related_name='tracking')
    
    # Tracking information
    courier_name = models.CharField(max_length=100, blank=True, null=True, help_text='e.g., Leopards, TCS, Call Courier')
    tracking_number = models.CharField(max_length=100, blank=True, null=True, help_text='Courier tracking number')
    estimated_delivery = models.DateField(blank=True, null=True)
    
    # Admin updates history
    status_updates = models.JSONField(default=list, help_text='List of status updates with timestamps and notes')
    
    # Live location (optional)
    current_location = models.CharField(max_length=200, blank=True, null=True, help_text='Current location of shipment')
    last_updated = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Order Tracking'
        verbose_name_plural = 'Order Tracking'
    
    def __str__(self):
        return f"Tracking for {self.order.order_id}"
    
    def add_status_update(self, status, note=None, location=None):
        """Add a new status update to tracking history"""
        update = {
            'status': status,
            'timestamp': models.DateTimeField(auto_now=True).__str__(),
            'note': note or '',
            'location': location or ''
        }
        
        if not self.status_updates:
            self.status_updates = []
        
        self.status_updates.append(update)
        
        # Also update the order's main status
        self.order.status = status
        self.order.save()
        
        # Update current location if provided
        if location:
            self.current_location = location
        
        self.save()
    
    @property
    def last_status(self):
        """Get the most recent status update"""
        if self.status_updates and len(self.status_updates) > 0:
            return self.status_updates[-1]
        return None
    
    @property
    def status_timeline(self):
        """Get all status updates in reverse chronological order"""
        if self.status_updates:
            return list(reversed(self.status_updates))
        return []
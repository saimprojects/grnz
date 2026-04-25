from rest_framework import serializers
from .models import OrderTracking
from apps.orders.models import GhostOrder

class OrderTrackingSerializer(serializers.ModelSerializer):
    order_id = serializers.ReadOnlyField(source='order.order_id')
    customer_name = serializers.ReadOnlyField(source='order.customer_name')
    customer_phone = serializers.ReadOnlyField(source='order.customer_phone')
    order_status = serializers.ReadOnlyField(source='order.status')
    order_total = serializers.ReadOnlyField(source='order.total_amount')
    created_at = serializers.ReadOnlyField(source='order.created_at')
    
    class Meta:
        model = OrderTracking
        fields = [
            'order_id', 'customer_name', 'customer_phone', 'order_status', 'order_total',
            'courier_name', 'tracking_number', 'estimated_delivery',
            'status_updates', 'current_location', 'last_updated', 'created_at'
        ]

class TrackingUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=GhostOrder.STATUS_CHOICES)
    note = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)
    
    def validate_status(self, value):
        valid_statuses = [choice[0] for choice in GhostOrder.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Choose from: {', '.join(valid_statuses)}")
        return value
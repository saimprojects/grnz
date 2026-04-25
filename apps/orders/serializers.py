from rest_framework import serializers
from .models import GhostOrder, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'product_name', 'variant_id', 'variant_details', 'quantity', 'unit_price', 'total_price']

class GhostOrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    full_address = serializers.ReadOnlyField()
    
    class Meta:
        model = GhostOrder
        fields = [
            'id', 'order_id', 'customer_name', 'customer_email', 'customer_phone',
            'province', 'city', 'main_address', 'street_number', 'house_number', 'landmark',
            'full_address', 'items', 'order_items', 'subtotal', 'delivery_charges',
            'total_amount', 'status', 'payment_status', 'payment_method',
            'notes', 'admin_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_id', 'subtotal', 'total_amount', 'created_at', 'updated_at']

class GhostOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GhostOrder
        fields = [
            'customer_name', 'customer_email', 'customer_phone',
            'province', 'city', 'main_address', 'street_number', 'house_number', 'landmark',
            'items', 'notes', 'delivery_charges', 'payment_method'
        ]
    
    def validate_items(self, value):
        if not value or len(value) == 0:
            raise serializers.ValidationError("At least one item is required")
        return value
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        delivery_charges = validated_data.pop('delivery_charges', 0)
        
        # Convert delivery_charges to float if it's string
        if isinstance(delivery_charges, str):
            delivery_charges = float(delivery_charges) if delivery_charges else 0
        
        # Calculate subtotal and product delivery charges
        subtotal = 0
        product_delivery_total = 0
        
        for item in items_data:
            # Get price - handle both string and number
            price = item.get('unit_price', item.get('price', 0))
            if isinstance(price, str):
                price = float(price)
            
            quantity = item.get('quantity', 1)
            if isinstance(quantity, str):
                quantity = int(quantity)
            
            subtotal += price * quantity
            
            # Get product delivery charges from database
            product_id = item.get('product_id')
            if product_id:
                from apps.products.models import Product
                try:
                    product = Product.objects.get(id=product_id)
                    if product.delivery_charges:
                        product_delivery_total += float(product.delivery_charges)
                except Product.DoesNotExist:
                    pass
        
        # Use max of product delivery total or custom delivery charges
        final_delivery_charges = max(product_delivery_total, float(delivery_charges))
        total_amount = subtotal + final_delivery_charges
        
        # Create order
        order = GhostOrder.objects.create(
            subtotal=subtotal,
            delivery_charges=final_delivery_charges,
            total_amount=total_amount,
            **validated_data
        )
        
        # Create order items
        for item in items_data:
            # Get values with proper type conversion
            unit_price = item.get('unit_price', item.get('price', 0))
            if isinstance(unit_price, str):
                unit_price = float(unit_price)
            
            quantity = item.get('quantity', 1)
            if isinstance(quantity, str):
                quantity = int(quantity)
            
            OrderItem.objects.create(
                order=order,
                product_id=item.get('product_id'),
                product_name=item.get('product_name'),
                variant_id=item.get('variant_id'),
                variant_details=item.get('variant_details', ''),
                quantity=quantity,
                unit_price=unit_price
            )
        
        return order

class TrackOrderSerializer(serializers.Serializer):
    order_id = serializers.CharField(max_length=20)
    
    def validate_order_id(self, value):
        if not GhostOrder.objects.filter(order_id=value).exists():
            raise serializers.ValidationError("Order not found")
        return value
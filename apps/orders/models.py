from django.db import models
import random
import string
from django.core.validators import MinValueValidator, MaxValueValidator

def generate_ghost_order_id():
    """Generate unique order ID like GHOST-XXXXXXXX"""
    return f"GHOST-{''.join(random.choices(string.digits, k=8))}"

class GhostOrder(models.Model):
    # Order status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
    ]
    
    PROVINCE_CHOICES = [
        ('punjab', 'Punjab'),
        ('sindh', 'Sindh'),
        ('kpk', 'Khyber Pakhtunkhwa'),
        ('balochistan', 'Balochistan'),
        ('gilgit', 'Gilgit-Baltistan'),
        ('kashmir', 'Azad Kashmir'),
        ('islamabad', 'Islamabad'),
    ]
    
    # Order ID
    order_id = models.CharField(max_length=20, unique=True, default=generate_ghost_order_id, editable=False)
    
    # Customer Information
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    
    # Address broken into parts
    province = models.CharField(max_length=50, choices=PROVINCE_CHOICES)
    city = models.CharField(max_length=100)
    main_address = models.TextField(help_text='Main address area / sector / colony name')
    street_number = models.CharField(max_length=50, blank=True, help_text='Street number / name')
    house_number = models.CharField(max_length=50, help_text='House / building / flat number')
    landmark = models.CharField(max_length=200, blank=True, help_text='Nearby landmark if any')
    
    # Order items stored as JSON (backward compatibility)
    items = models.JSONField(help_text='List of ordered items with product details', default=list, blank=True)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Order status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    
    # Additional info
    notes = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True, help_text='Internal admin notes')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Ghost Order'
        verbose_name_plural = 'Ghost Orders'
    
    def __str__(self):
        return f"{self.order_id} - {self.customer_name} - {self.status}"
    
    @property
    def full_address(self):
        """Return complete formatted address"""
        address_parts = []
        
        # House and street
        if self.house_number:
            address_parts.append(f"House #{self.house_number}")
        if self.street_number:
            address_parts.append(f"Street #{self.street_number}")
        
        # Main address
        if self.main_address:
            address_parts.append(self.main_address)
        
        # Landmark
        if self.landmark:
            address_parts.append(f"Near: {self.landmark}")
        
        # City and province
        city_province = self.city
        if self.province:
            province_name = dict(self.PROVINCE_CHOICES).get(self.province, self.province)
            city_province += f", {province_name}"
        address_parts.append(city_province)
        
        return ", ".join(address_parts)
    
    @property
    def has_free_shipping(self):
        """Check if order has free shipping"""
        return self.delivery_charges == 0
    
    @property
    def total_items_count(self):
        """Get total number of items in order"""
        return sum(item.quantity for item in self.order_items.all())

class OrderItem(models.Model):
    """Individual items in an order - for better querying"""
    order = models.ForeignKey(GhostOrder, on_delete=models.CASCADE, related_name='order_items')
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=200)
    variant_id = models.IntegerField(null=True, blank=True)
    variant_details = models.CharField(max_length=200, blank=True, help_text='e.g., Size: M, Color: Red')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Delivery charges for this specific item')
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity} - {self.order.order_id}"
    
    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
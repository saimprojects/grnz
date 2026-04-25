from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField
from ckeditor.fields import RichTextField
from apps.categories.models import Category

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = RichTextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Delivery Charges - New Field
    delivery_charges = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Delivery charges for this product. Leave empty or 0 for free shipping."
    )
    
    thumbnail = CloudinaryField('image', folder='products/thumbnails/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def final_price(self):
        """Return discounted price if available, else base price"""
        if self.discounted_price and self.discounted_price < self.base_price:
            return self.discounted_price
        return self.base_price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.discounted_price and self.discounted_price < self.base_price:
            discount = self.base_price - self.discounted_price
            return int((discount / self.base_price) * 100)
        return 0
    
    @property
    def has_free_shipping(self):
        """Check if product has free shipping"""
        return self.delivery_charges is None or self.delivery_charges == 0
    
    @property
    def delivery_charge_display(self):
        """Display delivery charges"""
        if self.has_free_shipping:
            return "Free Shipping"
        return f"Rs. {self.delivery_charges}"

class ProductVariant(models.Model):
    SIZE_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Double Extra Large'),
    ]
    
    COLOR_CHOICES = [
        ('Red', 'Red'),
        ('Blue', 'Blue'),
        ('Green', 'Green'),
        ('Black', 'Black'),
        ('White', 'White'),
        ('Yellow', 'Yellow'),
        ('Purple', 'Purple'),
        ('Pink', 'Pink'),
        ('Orange', 'Orange'),
        ('Brown', 'Brown'),
        ('Grey', 'Grey'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, null=True, blank=True)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, null=True, blank=True)
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    image = CloudinaryField('image', folder='products/variants/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['product', 'size', 'color']
        ordering = ['product', 'size', 'color']
    
    def __str__(self):
        variant_info = []
        if self.size:
            variant_info.append(self.size)
        if self.color:
            variant_info.append(self.color)
        variant_str = ' - '.join(variant_info) if variant_info else 'Default'
        return f"{self.product.name} ({variant_str})"
    
    @property
    def in_stock(self):
        return self.stock_quantity > 0

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image', folder='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.product.name} - Image {self.order}"
    
    def save(self, *args, **kwargs):
        # If this image is set as primary, unset other primary images for this product
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)
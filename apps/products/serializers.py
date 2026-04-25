from rest_framework import serializers
from .models import Product, ProductVariant, ProductImage
from apps.categories.serializers import CategorySerializer

class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'is_primary', 'order']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

class ProductVariantSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    in_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = ProductVariant
        fields = ['id', 'size', 'color', 'sku', 'price', 'stock_quantity', 'in_stock', 'image', 'image_url', 'is_active']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    final_price = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    thumbnail_url = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    delivery_charges = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    has_free_shipping = serializers.ReadOnlyField()
    delivery_charge_display = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'category_name',
            'base_price', 'discounted_price', 'final_price', 'discount_percentage',
            'delivery_charges', 'has_free_shipping', 'delivery_charge_display',
            'thumbnail', 'thumbnail_url', 'primary_image', 'is_active', 'is_featured', 'created_at'
        ]
    
    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            return obj.thumbnail.url
        return None
    
    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary and primary.image:
            return primary.image.url
        if obj.thumbnail:
            return obj.thumbnail.url
        return None

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    final_price = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    thumbnail_url = serializers.SerializerMethodField()
    delivery_charges = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    has_free_shipping = serializers.ReadOnlyField()
    delivery_charge_display = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category',
            'base_price', 'discounted_price', 'final_price', 'discount_percentage',
            'delivery_charges', 'has_free_shipping', 'delivery_charge_display',
            'thumbnail', 'thumbnail_url', 'variants', 'images',
            'is_active', 'is_featured', 'created_at', 'updated_at'
        ]
    
    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            return obj.thumbnail.url
        return None
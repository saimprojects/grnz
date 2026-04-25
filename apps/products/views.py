from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import Product, ProductVariant
from .serializers import ProductListSerializer, ProductDetailSerializer, ProductVariantSerializer

class ProductListAPIView(generics.ListAPIView):
    """Get all active products"""
    serializer_class = ProductListSerializer
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by min price
        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(base_price__gte=min_price)
        
        # Filter by max price
        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(base_price__lte=max_price)
        
        # Search by name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        
        # Filter featured products
        featured = self.request.query_params.get('featured')
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Order by
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering in ['price', '-price', 'created_at', '-created_at', 'name', '-name']:
            if ordering == 'price':
                queryset = queryset.order_by('base_price')
            elif ordering == '-price':
                queryset = queryset.order_by('-base_price')
            else:
                queryset = queryset.order_by(ordering)
        
        return queryset

class ProductDetailAPIView(generics.RetrieveAPIView):
    """Get single product by slug"""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'

class ProductVariantListAPIView(generics.ListAPIView):
    """Get all variants for a product"""
    serializer_class = ProductVariantSerializer
    
    def get_queryset(self):
        product_slug = self.kwargs.get('product_slug')
        return ProductVariant.objects.filter(
            product__slug=product_slug,
            is_active=True
        )

class FilterOptionsAPIView(APIView):
    """Get all filter options (categories, price range)"""
    
    def get(self, request):
        products = Product.objects.filter(is_active=True)
        
        # Get price range
        min_price = products.aggregate(models.Min('base_price'))['base_price__min'] or 0
        max_price = products.aggregate(models.Max('base_price'))['base_price__max'] or 0
        
        return Response({
            'price_range': {
                'min': float(min_price),
                'max': float(max_price)
            }
        })
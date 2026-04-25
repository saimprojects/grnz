from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Category
from .serializers import CategorySerializer

class CategoryListAPIView(generics.ListAPIView):
    """Get all active main categories (parent=None)"""
    queryset = Category.objects.filter(is_active=True, parent=None)
    serializer_class = CategorySerializer

class AllCategoriesAPIView(generics.ListAPIView):
    """Get all active categories (including subcategories)"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer

class CategoryDetailAPIView(generics.RetrieveAPIView):
    """Get single category by slug"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'

class CategoryProductsAPIView(APIView):
    """Get all products under a category (including subcategories)"""
    
    def get(self, request, slug):
        try:
            category = Category.objects.get(slug=slug, is_active=True)
            
            # Get all subcategory IDs
            category_ids = [category.id]
            subcategories = category.children.filter(is_active=True)
            for subcat in subcategories:
                category_ids.append(subcat.id)
                # Get sub-subcategories
                for subsubcat in subcat.children.filter(is_active=True):
                    category_ids.append(subsubcat.id)
            
            # Import Product model here to avoid circular import
            from apps.products.models import Product
            products = Product.objects.filter(
                category_id__in=category_ids, 
                is_active=True
            )
            
            # Serialize products (we'll create product serializer later)
            from apps.products.serializers import ProductListSerializer
            product_data = ProductListSerializer(products, many=True).data
            
            return Response({
                'category': CategorySerializer(category).data,
                'products': product_data,
                'product_count': products.count()
            })
            
        except Category.DoesNotExist:
            return Response(
                {'error': 'Category not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class CategoryCreateAPIView(generics.CreateAPIView):
    """Create new category (Admin only - we'll add permission later)"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryUpdateAPIView(generics.UpdateAPIView):
    """Update category (Admin only)"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

class CategoryDeleteAPIView(generics.DestroyAPIView):
    """Delete category (Admin only)"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
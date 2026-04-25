from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 
            'name', 
            'slug', 
            'parent', 
            'parent_name',
            'image', 
            'image_url',
            'is_active', 
            'children', 
            'created_at',
            'updated_at'
        ]
    
    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.filter(is_active=True), many=True).data
        return []
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None
    
    def get_parent_name(self, obj):
        if obj.parent:
            return obj.parent.name
        return None
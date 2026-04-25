from rest_framework import serializers
from .models import Contact, NewsletterSubscriber

class ContactSerializer(serializers.ModelSerializer):
    subject_type_label = serializers.ReadOnlyField()
    priority_label = serializers.ReadOnlyField()
    response_status = serializers.ReadOnlyField()
    created_at_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Contact
        fields = [
            'id', 'name', 'email', 'phone',
            'subject_type', 'subject_type_label', 'subject', 'message',
            'attachment', 'priority', 'priority_label',
            'is_resolved', 'response_status',
            'admin_response', 'admin_response_at', 'responded_by',
            'created_at', 'created_at_formatted', 'updated_at'
        ]
        read_only_fields = ['is_resolved', 'resolved_at', 'admin_response', 'admin_response_at', 'responded_by']
    
    def get_created_at_formatted(self, obj):
        return obj.created_at.strftime("%B %d, %Y at %I:%M %p")

class ContactCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'subject_type', 'subject', 'message', 'attachment']
    
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters")
        return value.strip()
    
    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters")
        return value.strip()
    
    def validate_subject(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Subject must be at least 3 characters")
        return value.strip()

class ContactResponseSerializer(serializers.Serializer):
    """Serializer for admin response"""
    response = serializers.CharField(required=True, min_length=5)
    
    def validate_response(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Response must be at least 5 characters")
        return value.strip()

class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = ['id', 'email', 'is_active', 'subscribed_at']
        read_only_fields = ['subscribed_at']
    
    def validate_email(self, value):
        if NewsletterSubscriber.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already subscribed")
        return value
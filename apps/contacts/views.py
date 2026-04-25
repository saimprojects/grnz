from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Contact, NewsletterSubscriber
from .serializers import (
    ContactSerializer, 
    ContactCreateSerializer, 
    ContactResponseSerializer,
    NewsletterSubscriberSerializer
)

class ContactCreateAPIView(generics.CreateAPIView):
    """Submit a contact form message"""
    serializer_class = ContactCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        contact = serializer.save()
        
        # Here you can add email notification to admin
        # send_email_notification(contact)
        
        return Response({
            'success': True,
            'message': 'Your message has been sent successfully! We will get back to you soon.',
            'contact_id': contact.id,
            'reference': f"REF-{contact.id:06d}"
        }, status=status.HTTP_201_CREATED)

class ContactListAPIView(generics.ListAPIView):
    """List all contacts (Admin only)"""
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

class ContactDetailAPIView(generics.RetrieveAPIView):
    """Get single contact (Admin only)"""
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    lookup_field = 'id'

class AdminContactResponseAPIView(APIView):
    """Admin response to contact message"""
    
    def post(self, request, contact_id):
        contact = get_object_or_404(Contact, id=contact_id)
        
        serializer = ContactResponseSerializer(data=request.data)
        if serializer.is_valid():
            response_text = serializer.validated_data['response']
            
            from django.utils import timezone
            contact.admin_response = response_text
            contact.admin_response_at = timezone.now()
            contact.responded_by = request.user.username if request.user.is_authenticated else 'Admin'
            contact.is_resolved = True
            contact.resolved_at = timezone.now()
            contact.save()
            
            # Here you can send email to user with response
            # send_response_email(contact)
            
            return Response({
                'success': True,
                'message': 'Response sent successfully',
                'contact': ContactSerializer(contact).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContactResolveAPIView(APIView):
    """Mark contact as resolved without response"""
    
    def post(self, request, contact_id):
        contact = get_object_or_404(Contact, id=contact_id)
        contact.mark_as_resolved()
        
        return Response({
            'success': True,
            'message': 'Contact marked as resolved'
        })

class MyContactsAPIView(APIView):
    """Get all contacts by email (for users to check their submissions)"""
    
    def get(self, request):
        email = request.query_params.get('email')
        
        if not email:
            return Response({
                'success': False,
                'error': 'Email parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        contacts = Contact.objects.filter(email=email).order_by('-created_at')
        serializer = ContactSerializer(contacts, many=True)
        
        return Response({
            'success': True,
            'count': contacts.count(),
            'contacts': serializer.data
        })

class ContactStatsAPIView(APIView):
    """Get contact statistics (Admin only)"""
    
    def get(self, request):
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        stats = {
            'total': Contact.objects.count(),
            'pending': Contact.objects.filter(is_resolved=False).count(),
            'resolved': Contact.objects.filter(is_resolved=True).count(),
            'urgent': Contact.objects.filter(priority='urgent', is_resolved=False).count(),
            'by_subject': dict(Contact.objects.values_list('subject_type').annotate(count=Count('id'))),
            'by_priority': dict(Contact.objects.values_list('priority').annotate(count=Count('id'))),
            'last_7_days': Contact.objects.filter(created_at__gte=week_ago).count(),
            'last_30_days': Contact.objects.filter(created_at__gte=month_ago).count(),
            'avg_response_time': self.get_avg_response_time(),
        }
        
        return Response(stats)
    
    def get_avg_response_time(self):
        """Calculate average response time in hours"""
        from django.db.models import F, ExpressionWrapper, fields, Avg
        from django.db.models.functions import ExtractHour
        
        responded = Contact.objects.filter(
            admin_response_at__isnull=False,
            created_at__isnull=False
        )
        
        if responded.count() == 0:
            return None
        
        # Calculate difference in hours
        total_hours = 0
        for contact in responded:
            diff = contact.admin_response_at - contact.created_at
            total_hours += diff.total_seconds() / 3600
        
        return round(total_hours / responded.count(), 1)

# Newsletter Views
class NewsletterSubscribeAPIView(generics.CreateAPIView):
    """Subscribe to newsletter"""
    serializer_class = NewsletterSubscriberSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Successfully subscribed to newsletter!'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NewsletterUnsubscribeAPIView(APIView):
    """Unsubscribe from newsletter"""
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({
                'success': False,
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subscriber = NewsletterSubscriber.objects.get(email=email)
            subscriber.is_active = False
            subscriber.save()
            
            return Response({
                'success': True,
                'message': 'Successfully unsubscribed from newsletter'
            })
        except NewsletterSubscriber.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Email not found in subscribers'
            }, status=status.HTTP_404_NOT_FOUND)
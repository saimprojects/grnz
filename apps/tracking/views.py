from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import OrderTracking
from .serializers import OrderTrackingSerializer, TrackingUpdateSerializer
from apps.orders.models import GhostOrder

class TrackOrderByIDAPIView(APIView):
    """Track order by order ID (Ghost ID)"""
    
    def get(self, request, order_id):
        try:
            order = GhostOrder.objects.get(order_id=order_id)
            
            # Get or create tracking record
            tracking, created = OrderTracking.objects.get_or_create(order=order)
            
            serializer = OrderTrackingSerializer(tracking)
            return Response({
                'success': True,
                'tracking': serializer.data
            })
        except GhostOrder.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Order not found. Please check your Order ID.'
            }, status=status.HTTP_404_NOT_FOUND)

class TrackOrderByPhoneAPIView(APIView):
    """Track orders by phone number (returns all orders for that phone)"""
    
    def get(self, request):
        phone = request.query_params.get('phone')
        
        if not phone:
            return Response({
                'success': False,
                'error': 'Phone number is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        orders = GhostOrder.objects.filter(customer_phone=phone)
        
        if not orders.exists():
            return Response({
                'success': False,
                'error': 'No orders found for this phone number'
            }, status=status.HTTP_404_NOT_FOUND)
        
        tracking_data = []
        for order in orders:
            tracking, _ = OrderTracking.objects.get_or_create(order=order)
            tracking_data.append(OrderTrackingSerializer(tracking).data)
        
        return Response({
            'success': True,
            'count': orders.count(),
            'orders': tracking_data
        })

class AddTrackingUpdateAPIView(APIView):
    """Add a new tracking update to an order (Admin only)"""
    
    def post(self, request, order_id):
        try:
            order = GhostOrder.objects.get(order_id=order_id)
            tracking, created = OrderTracking.objects.get_or_create(order=order)
            
            serializer = TrackingUpdateSerializer(data=request.data)
            if serializer.is_valid():
                # Add the status update
                update = {
                    'status': serializer.validated_data['status'],
                    'timestamp': None,  # Will be set in model method
                    'note': serializer.validated_data.get('note', ''),
                    'location': serializer.validated_data.get('location', '')
                }
                
                if not tracking.status_updates:
                    tracking.status_updates = []
                
                # Add timestamp
                from django.utils import timezone
                update['timestamp'] = timezone.now().isoformat()
                
                tracking.status_updates.append(update)
                
                # Update order main status
                order.status = serializer.validated_data['status']
                order.save()
                
                # Update current location if provided
                if serializer.validated_data.get('location'):
                    tracking.current_location = serializer.validated_data['location']
                
                tracking.save()
                
                return Response({
                    'success': True,
                    'message': 'Tracking update added successfully',
                    'current_status': order.status,
                    'all_updates': tracking.status_updates
                })
            else:
                return Response({
                    'success': False,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except GhostOrder.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)

class UpdateCourierInfoAPIView(APIView):
    """Update courier information for an order"""
    
    def patch(self, request, order_id):
        try:
            order = GhostOrder.objects.get(order_id=order_id)
            tracking, created = OrderTracking.objects.get_or_create(order=order)
            
            courier_name = request.data.get('courier_name')
            tracking_number = request.data.get('tracking_number')
            estimated_delivery = request.data.get('estimated_delivery')
            
            if courier_name:
                tracking.courier_name = courier_name
            if tracking_number:
                tracking.tracking_number = tracking_number
            if estimated_delivery:
                tracking.estimated_delivery = estimated_delivery
            
            tracking.save()
            
            return Response({
                'success': True,
                'message': 'Courier information updated',
                'courier_name': tracking.courier_name,
                'tracking_number': tracking.tracking_number,
                'estimated_delivery': tracking.estimated_delivery
            })
            
        except GhostOrder.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)

class TrackingTimelineAPIView(APIView):
    """Get only timeline of tracking updates for an order"""
    
    def get(self, request, order_id):
        try:
            order = GhostOrder.objects.get(order_id=order_id)
            tracking, created = OrderTracking.objects.get_or_create(order=order)
            
            return Response({
                'success': True,
                'order_id': order.order_id,
                'current_status': order.status,
                'timeline': tracking.status_timeline,
                'current_location': tracking.current_location,
                'estimated_delivery': tracking.estimated_delivery
            })
            
        except GhostOrder.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)
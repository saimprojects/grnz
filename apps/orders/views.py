from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import GhostOrder
from .serializers import GhostOrderSerializer, GhostOrderCreateSerializer, TrackOrderSerializer

class OrderCreateAPIView(generics.CreateAPIView):
    """Create a new ghost order"""
    serializer_class = GhostOrderCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Order placed successfully',
            'order_id': order.order_id,
            'status': order.status,
            'total_amount': order.total_amount,
            'tracking_url': f'/track/{order.order_id}'
        }, status=status.HTTP_201_CREATED)

class OrderDetailAPIView(APIView):
    """Get order details by order_id (no auth required)"""
    
    def get(self, request, order_id):
        try:
            order = GhostOrder.objects.get(order_id=order_id)
            serializer = GhostOrderSerializer(order)
            return Response(serializer.data)
        except GhostOrder.DoesNotExist:
            return Response({
                'error': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)

class OrderListByEmailAPIView(APIView):
    """Get all orders for an email address"""
    
    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response({
                'error': 'Email parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        orders = GhostOrder.objects.filter(customer_email=email)
        serializer = GhostOrderSerializer(orders, many=True)
        return Response(serializer.data)

class OrderStatusUpdateAPIView(APIView):
    """Update order status (admin only - will add permission later)"""
    
    def patch(self, request, order_id):
        try:
            order = GhostOrder.objects.get(order_id=order_id)
            new_status = request.data.get('status')
            
            if new_status and new_status in dict(GhostOrder.STATUS_CHOICES):
                order.status = new_status
                order.save()
                
                return Response({
                    'success': True,
                    'order_id': order.order_id,
                    'status': order.status,
                    'message': f'Order status updated to {new_status}'
                })
            else:
                return Response({
                    'error': 'Invalid status'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except GhostOrder.DoesNotExist:
            return Response({
                'error': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.orders.models import GhostOrder
from .models import OrderTracking

@receiver(post_save, sender=GhostOrder)
def create_tracking_for_order(sender, instance, created, **kwargs):
    """Automatically create tracking record when order is created"""
    if created:
        OrderTracking.objects.create(order=instance)
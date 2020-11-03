from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@receiver(post_save, sender=Order)
def order_notification(sender, **kwargs):
    if "instance" in kwargs:
        instance = kwargs["instance"]
        channel_layer = get_channel_layer()
        group_name = 'order_%s' % instance.seller.id
        async_to_sync(channel_layer.group_send)(
            group_name, {"type": "send_order",
                         "id": instance.pk
                         })

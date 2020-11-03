from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from crm.models import Profile
from .models import Message, ComplatedTask
from .utils import WhatsAppAPI
from django.contrib.auth.models import User


@receiver(post_save, sender=Message)
def message_notification(sender, **kwargs):
    if "instance" in kwargs:
        instance = kwargs["instance"]
        if instance.photo:
            integration = instance.lead.integration
            token = integration.api_token
            account_id = integration.api_id
            chat_id = instance.lead.customer.social_id
            photo_url = instance.get_photo_url()
            photo_name = instance.get_photo_name()
            api =  WhatsAppAPI.sendPhoto(
                account_id, token, chat_id, photo_url, photo_name)
            apiId = api.get('id')
            ComplatedTask.objects.create(
                message_id=instance.id, apiId=apiId)
    return True

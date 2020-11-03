import os
import json
from django.conf import settings
from django.db import models
from crm.models import Lead


# Список сообщении
class Message(models.Model):
    lead = models.ForeignKey(
        Lead, related_name='messages_lead',
        on_delete=models.CASCADE)
    fromMe = models.BooleanField(default=False)
    message = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to="images", blank=True, null=True)
    photo_url = models.URLField(max_length=380, blank=True, null=True)
    ptt_url = models.URLField(max_length=380, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    api_id = models.CharField(max_length=80, blank=True, null=True)
    
    def get_photo_name(self):
        return os.path.basename(self.photo.name)

    def get_photo_url(self):
        if settings.DEBUG:
            host = 'https://tasty-insect-60.loca.lt'
        else:
            host = 'https://tasty-insect-60.loca.lt'
        return host + self.photo.url

    @property
    def get_message(self):
        return json.loads(self.message)

    class Meta:
        db_table = "messages"


# Статус задачи
class ComplatedTask(models.Model):
    message = models.ForeignKey(
        Message, related_name='complated_task_message',
        on_delete=models.CASCADE)
    apiId = models.CharField(max_length=180, blank=True, null=True)

    class Meta:
        db_table = "complated_task"
import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from crm.models import Lead


class MessengerConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.sender = self.scope['url_route']['kwargs']['user']
        
        if self.user.profile.type == 3:
            self.room_group_name = 'manager_%s' % self.sender
        else:
            self.room_group_name = 'leaders_%s' % self.user.profile.company.id
            
        # join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        # accept connection
        self.accept()

    def disconnect(self, close_code):
        # leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # receive message from WebSocket
    def receive(self, text_data):
        data_json = json.loads(text_data)
        message = data_json.get('message', None)
        lead = data_json.get('lead', None)
        data = {
            'type': 'send_message',
            'id': message,
            'lead': lead,
            'fromMe': True
        }
        async_to_sync(self.channel_layer.group_send)(
            'leaders_%s' % self.user.profile.company.id, data
        )
        if self.user.profile.type == 3:
            async_to_sync(self.channel_layer.group_send)(
                'manager_%s' % self.sender, data
            )
        else:
            lead_q = Lead.objects.get(id=lead)
            manager = lead_q.manager
            async_to_sync(self.channel_layer.group_send)(
                'manager_%s' % manager.id, data
            )
            
        

    # receive message from room group
    def send_message(self, event):
        self.send(text_data=json.dumps(event))

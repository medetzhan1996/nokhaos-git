import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class FigmaConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.id = self.scope['url_route']['kwargs']['id']
        self.seller = self.scope['url_route']['kwargs']['author_id']
        self.customer = self.scope["session"]["client_auth"]
        self.room_group_name = 'shop_%s' % self.id
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
        text_data_json = json.loads(text_data)
        product = text_data_json.get('product')
        preview_text = text_data_json.get('preview_text', None)
        product_material = text_data_json.get('product_material', None)
        phone_number = text_data_json.get('phone_number', None)
        preview_file = text_data_json.get('preview_file', None)
        order_id = 2

        # send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'preview_text': preview_text,
                'product': product,
                'product_material': product_material,
                'phone_number': phone_number,
                'seller': self.seller,
                'customer': self.customer,
                'preview_file': preview_file,
                'order_id': order_id
            }
        )

    # receive message from room group
    def chat_message(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps(event))

import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class OrderConsumer(WebsocketConsumer):
    def connect(self):
        self.channel = self.scope['url_route']['kwargs']['channel']
        self.room_group_name = 'order_%s' % self.channel
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
        pass
        """data_json = json.loads(text_data)
        product = data_json.get('product')
        preview_text = data_json.get('preview_text', None)
        product_material = data_json.get('product_material', None)
        phone_number = data_json.get('phone_number', None)
        preview_file = data_json.get('preview_file', None)
        order_id = 5

        # send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'send_order',
                'seller': self.seller,
                'preview_text': preview_text,
                'product': product,
                'product_material': product_material,
                'phone_number': phone_number,
                'preview_file': preview_file,
                'order_id': order_id
            }
        ) """

    # receive message from room group
    def send_order(self, event):
        self.send(text_data=json.dumps(event))

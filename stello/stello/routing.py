from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import social_messenger.routing
application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            social_messenger.routing.websocket_urlpatterns
        )
    )
})

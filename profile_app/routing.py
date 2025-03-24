# from django.urls import re_path
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from .consumers import ChatConsumer

# websocket_urlpatterns = [
#     re_path(r"ws/chat/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),
# ]

# application = ProtocolTypeRouter({
#     "websocket": AuthMiddlewareStack(
#         URLRouter(websocket_urlpatterns)
#     ),
# })
# from django.urls import re_path
# from .consumers import ChatConsumer

# websocket_urlpatterns = [
#     re_path(r"ws/chat/(?P<username>\w+)/$", ChatConsumer.as_asgi()),
# ]
from django.urls import re_path
from profile_app.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<username>\w+)/$", ChatConsumer.as_asgi()),
]

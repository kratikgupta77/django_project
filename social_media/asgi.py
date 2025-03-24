"""
ASGI config for social_media project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""
# import os
# import django
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', "social_media.settings")

# django.setup()  

# import profile_app.routing

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(profile_app.routing.websocket_urlpatterns)
#     ),
# })
# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from profile_app.routing import websocket_urlpatterns

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "social_media.settings")

# application = ProtocolTypeRouter(
#     {
#         "http": get_asgi_application(),
#         "websocket": URLRouter(websocket_urlpatterns),
#     }
# )

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import profile_app.routing  # Import WebSocket routes

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "social_media.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(profile_app.routing.websocket_urlpatterns)
    ),
})

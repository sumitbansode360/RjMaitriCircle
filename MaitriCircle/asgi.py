import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MaitriCircle.settings')

# Initialize Django ASGI application early
django_asgi_app = get_asgi_application()

# Now import other dependencies
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from chat import routing as chat_routing
from notification import routing as notification_routing

# Combine both routing patterns
websocket_urlpatterns = chat_routing.websocket_urlpatterns + notification_routing.websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
    ),
})

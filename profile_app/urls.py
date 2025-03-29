from django.urls import path
from .views import profile_view, messages_view, logout_view, send_message, fetch_messages,update_public_key

urlpatterns = [
    path("profile/", profile_view, name="profile_view"),
    path("logout/", logout_view, name="logout"),
    path("messages/", messages_view, name="messages_view"),
    path("messages/send/", send_message, name="send_message"),
    path("messages/fetch/", fetch_messages, name="fetch_messages"),  
    path("profile/update_public_key/", update_public_key, name="update_public_key"),

]

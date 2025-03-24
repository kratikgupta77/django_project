from django.urls import path
from .views import profile_view, messages_view, logout_view, send_message

urlpatterns = [
    path("profile/", profile_view, name="profile_view"),
    path("logout/", logout_view, name="logout"),
    path("messages/", messages_view, name="messages_view"),
    path("messages/send/", send_message, name="send_message"),
]

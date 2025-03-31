from django.urls import path
from .views import (
    profile_view, messages_view, logout_view, send_message, fetch_messages, update_public_key,
    group_list_view, create_group, group_detail_view, send_group_message, fetch_group_messages,
    join_group, leave_group, delete_group
)

urlpatterns = [
    path("profile/", profile_view, name="profile_view"),
    path("logout/", logout_view, name="logout"),
    path("messages/", messages_view, name="messages_view"),
    path("messages/send/", send_message, name="send_message"),
    path("messages/fetch/", fetch_messages, name="fetch_messages"),
    path("profile/update_public_key/", update_public_key, name="update_public_key"),
    
    # --- Group Messaging URLs ---
    path("groups/", group_list_view, name="group_list_view"),
    path("groups/create/", create_group, name="create_group"),
    path("groups/<int:group_id>/", group_detail_view, name="group_detail"),
    path("groups/<int:group_id>/send/", send_group_message, name="send_group_message"),
    path("groups/<int:group_id>/fetch/", fetch_group_messages, name="fetch_group_messages"),
    path("groups/<int:group_id>/join/", join_group, name="join_group"),
    path("groups/<int:group_id>/leave/", leave_group, name="leave_group"),
    path("groups/<int:group_id>/delete/", delete_group, name="delete_group"),
]

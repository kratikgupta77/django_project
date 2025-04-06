from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (profile_view, messages_view, logout_view, send_message, update_public_key,
    group_list_view, create_group, group_detail_view, send_group_message, fetch_group_messages,
    join_group, leave_group, delete_group,send_reset_otp,verify_reset_otp,fetch_messages,get_public_key,verify_delete_otp,send_delete_otp)

urlpatterns = [
    path("profile/", profile_view, name="profile_view"),
    path("logout/", logout_view, name="logout"),
    path("messages/", messages_view, name="messages_view"),
    path("messages/send/", send_message, name="send_message"),
    path("messages/fetch/", fetch_messages, name="fetch_messages"),
    path("profile/update_public_key/", update_public_key, name="update_public_key"),
    path('delete-account/',send_delete_otp , name='delete_account'),
    path('confirm-delete/', verify_delete_otp, name='verify_delete_otp'),
    path("get_public_key/<str:username>/", get_public_key, name="get_public_key"),

    # --- Group Messaging URLs ---
    path("groups/", group_list_view, name="group_list_view"),
    path("groups/create/", create_group, name="create_group"),
    path("groups/<int:group_id>/", group_detail_view, name="group_detail"),
    path("groups/<int:group_id>/send/", send_group_message, name="send_group_message"),
    path("groups/<int:group_id>/fetch/", fetch_group_messages, name="fetch_group_messages"),
    path("groups/<int:group_id>/join/", join_group, name="join_group"),
    path("groups/<int:group_id>/leave/", leave_group, name="leave_group"),
    path("groups/<int:group_id>/delete/", delete_group, name="delete_group"),
    path("reset-password/", send_reset_otp, name="send_reset_otp"),
    path("verify-reset-otp/", verify_reset_otp, name="verify_reset_otp"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
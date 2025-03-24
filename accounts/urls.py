from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.urls import path
from .views import messaging_home, chat_view

urlpatterns = [
    path('register/', views.register, name='register'),
    # Use Django’s built-in LoginView; specify a custom template:
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('profile/', views.profile, name='profile'),
    path('messages/', messaging_home, name='messages_home'),
    path('messages/<str:username>/', chat_view, name='chat'),
    path('custom-admin/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('custom-admin/manage-users/', views.manage_users, name='manage_users'),
    path('custom-admin/manage-users/edit/<int:user_id>/', views.edit_user, name='edit_user'),  # Add this

]


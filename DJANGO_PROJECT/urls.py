from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include("social_media.urls")),  # Existing app for login/signup
    path('', include("profile_app.urls")),  # Profile management app
]

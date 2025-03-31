# p2pmarketplace/urls.py
from django.urls import path
from .views import api

urlpatterns = [
    path("api/", api, name="p2p_api"),
]

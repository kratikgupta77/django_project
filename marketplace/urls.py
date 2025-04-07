from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.marketplace_home, name='marketplace_home'),
    path('sell/', views.sell_item, name='sell_item'),
    path('artifacts/', views.artifact_list, name='artifact_list'),
    path('artifact/<int:pk>/', views.artifact_detail, name='artifact_detail'),
    path('artifact/<int:pk>/buy/', views.simulate_payment, name='simulate_payment'),
    path('payments/', views.payment_history, name='payment_history'),
    path('upload-public-key/', views.upload_public_key, name='upload_public_key'),

]

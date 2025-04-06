from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from .views import home, signup_view, login_view, logout_view

from django.urls import path, include
from .views import home, signup_view, login_view, logout_view,activate_account

urlpatterns = [
    path('', home, name='frontpage'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', include("profile_app.urls")), 
    path('marketplace/', include("marketplace.urls")), 
    path('activate/<uidb64>/<token>/', activate_account, name='activate_account'),

    path('admin/', admin.site.urls), 
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

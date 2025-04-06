from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from profile_app.models import BannedEmail

# Custom action to ban unverified users
def ban_unverified_users(modeladmin, request, queryset):
    for user in queryset:
        if not user.is_active:
            BannedEmail.objects.get_or_create(email=user.email)
            user.delete()
ban_unverified_users.short_description = "Ban and delete selected unverified users"

# Customizing the User admin
class CustomUserAdmin(UserAdmin):
    actions = [ban_unverified_users]
    list_display = ('username', 'email', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')

# Unregister default and register custom
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Movie, UserProfile

# Register your models here.

# Inline UserProfile in User Admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

# Extend User Admin
class ExtendedUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, ExtendedUserAdmin)

# Register Movie
admin.site.register(Movie)
# This will allow the Movie model to be managed through the Django admin interface.
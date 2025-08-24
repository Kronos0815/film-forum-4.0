from django.contrib import admin
from .models import MasterPassword

# Das Masterpasswort kann vorerst nur über das Admin-Interface geändert werden.

@admin.register(MasterPassword)
class MasterPasswordAdmin(admin.ModelAdmin):
    list_display = ('password', 'updated_at')
    fields = ('password',)
    
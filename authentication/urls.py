from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('', views.master_login, name='master_login'),
    path('logout/', views.logout, name='logout'),  # Logout URL hinzufügen
]
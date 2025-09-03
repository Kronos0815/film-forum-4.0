from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.profile_selection, name='selection'),
    path('select/<int:user_id>/', views.select_profile, name='select'),
    path("create/", views.show_create_profile, name="show_create_profile"),
    path("create/submit/", views.create_profile, name="create_profile"),
]
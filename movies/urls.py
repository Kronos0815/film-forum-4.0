from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.user_dashboard, name='user_dashboard'),  # Hauptseite ist jetzt user_dashboard
    path('list/', views.movie_list, name='movie_list'),     # Fallback für alte Links
    path('vote_search/<str:movie_id>/<str:movie_title>/', views.movie_vote_search, name='movie_vote_search'),
    path('unvote/<str:movie_id>/', views.movie_unvote, name='movie_unvote'),
    path('movie/<str:movie_id>/', views.movie_page, name='movie_page'),  
]

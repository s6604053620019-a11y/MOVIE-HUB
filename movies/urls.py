from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='home'),
    path('movie/<int:tmdb_id>/', views.movie_detail, name='movie_detail'),
    path('movie/<int:tmdb_id>/like/', views.toggle_like, name='toggle_like'),
    path('movie/<int:tmdb_id>/watchlist/', views.toggle_watchlist, name='toggle_watchlist'),
]

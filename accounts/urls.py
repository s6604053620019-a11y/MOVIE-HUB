from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('signup/', views.signup, name='signup'),
    path('user/<str:username>/', views.public_profile, name='public_profile'),
    path('user/<str:username>/follow/', views.toggle_follow, name='toggle_follow'),
    path('members/', views.members_list, name='members'),
    path('activity/', views.activity_feed, name='activity_feed'),
]

from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path
from movies.views import movie_list, movie_detail
from accounts.views import signup_view, profile_view  # <--- 1. ต้องมีบรรทัดนี้
from movies.views import movie_list, movie_detail, toggle_like
from movies.views import movie_list, movie_detail, toggle_like, toggle_watchlist
from django.conf import settings             # <--- เพิ่ม 1
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', movie_list),
    path('movie/<int:movie_id>/', movie_detail, name='movie_detail'),
    path('signup/', signup_view, name='signup'), # <--- 2. ต้องมีบรรทัดนี้path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('movie/<int:movie_id>/like/', toggle_like, name='toggle_like'),
    path('', movie_list, name='home'),
    path('profile/', profile_view, name='profile'),
    path('movie/<int:movie_id>/watchlist/', toggle_watchlist, name='toggle_watchlist'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
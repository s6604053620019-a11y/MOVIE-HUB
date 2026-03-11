from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'followers_count', 'following_count')
    search_fields = ('user__username',)
    filter_horizontal = ('following',)

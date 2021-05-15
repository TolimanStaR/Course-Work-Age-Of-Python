from django.contrib import admin

from .models import *


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['status', ]


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    pass

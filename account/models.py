from django.db import models
from django.contrib.auth.models import User


class UserProfile(User):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    status = models.CharField(max_length=100, blank=True)
    profile_photo = models.ImageField(upload_to='profile_images/', default='profile_images/default_avatar.png')
    profile_background = models.ImageField(upload_to='profile_background_images/', blank=True)
    friends = models.ManyToManyField(to='UserProfile', blank=True)


class FriendRequest(models.Model):
    from_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='outgoing_friend_requests')
    to_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='incoming_friend_requests')

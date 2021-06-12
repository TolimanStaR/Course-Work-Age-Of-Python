from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class University(models.TextChoices):
    HSE = 'HSE', _('Высшая школа экономики')
    UNN = 'UNN', _('Университет им. Лобачевского')
    PT = 'PT', _('Нижегородский политехнический университет')
    OTHER = 'OTHER', _('-')


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    status = models.CharField(max_length=100, blank=True)
    phone = PhoneNumberField(default='', blank=True)
    profile_photo = models.ImageField(upload_to='profile_images/', default='profile_images/default_avatar.png')
    profile_background = models.ImageField(upload_to='profile_background_images/', blank=True)
    friends = models.ManyToManyField(to='UserProfile', blank=True, related_name='friends_list')
    university = models.TextField(default=University.OTHER, choices=University.choices)
    website = models.URLField(default='', blank=True)
    address = models.CharField(default='-', max_length=50, blank=True)
    github = models.CharField(max_length=100, default='', blank=True)
    twitter = models.CharField(max_length=100, default='', blank=True)
    inst = models.CharField(max_length=100, default='', blank=True)
    facebook = models.CharField(max_length=100, default='', blank=True)

    def get_university(self):
        d = dict()
        for elem in University.choices:
            d[elem[0]] = elem[1]
        return d[self.university]


class FriendRequest(models.Model):
    from_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='outgoing_friend_requests')
    to_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='incoming_friend_requests')

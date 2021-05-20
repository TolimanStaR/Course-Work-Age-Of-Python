from django.urls import path

from .views import *

urlpatterns = [

    path('channel_create/',
         ChannelCreateView.as_view(),
         name='create_channel'),

    path('channel_create_confirm/',
         ChannelCreateFormHandle.as_view(),
         name='channel_create_confirm'),

    path('channel/<slug:slug>/',
         ChannelView.as_view(),
         name='channel'),

    path('mychannel',
         ChannelView.as_view(),
         name='my_channel'),

    path('channel_edit/<slug:slug>/',
         ChannelUpdateView.as_view(),
         name='update_channel'),
    #
    # path('channel_update_confirm/',
    #      ChannelUpdateView.as_view(),
    #      name='channel_update_confirm'),
]

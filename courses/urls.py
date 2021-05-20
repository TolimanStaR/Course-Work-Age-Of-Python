from django.urls import path

from .views import *

urlpatterns = [

    path('channel_create/',
         ChannelCreateView.as_view(),
         name='create_channel'),

    path('channel_create_conform/',
         ChannelCreateFormHandle.as_view(),
         name='channel_create_confirm'),

    path('channel/<slug:slug>/',
         ChannelView.as_view(),
         name='channel'),

    path('mychannel',
         ChannelView.as_view(),
         name='my_channel'),
]

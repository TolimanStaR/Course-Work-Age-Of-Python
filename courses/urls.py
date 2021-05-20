from django.urls import path

from .views import *

urlpatterns = [

    path('channel/create/',
         ChannelCreateView.as_view(),
         name='create_channel'),


    path('channel/<slug:slug>/',
         ChannelView.as_view(),
         name='channel'),

    path('mychannel',
         ChannelView.as_view(),
         name='my_channel'),
]


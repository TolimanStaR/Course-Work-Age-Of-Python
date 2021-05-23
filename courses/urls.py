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

    path('channel/<slug:slug>/update/',
         ChannelUpdateView.as_view(),
         name='update_channel'),

    path('channel/<slug:slug>/subscribers/',
         ChannelSubscribersListView.as_view(),
         name='channel_subscribers'),

    path('channel/<slug:slug>/subscribers/<str:username>/manage/',
         ManageChannelSubscriber.as_view(),
         name='channel_manage_subscriber'),

    path('channel/<slug:slug>/subscribe/',
         ChannelSubscribeFormHandle.as_view(),
         name='channel_subscribe'),

    path('channel/<slug:slug>/subscribe_delete/<str:username>/',
         ChannelDeleteSubscribeFormHandle.as_view(),
         name='channel_delete_subscribe'),

    path('channel/<slug:slug>/course_list_edit/',
         ChannelCoursesListView.as_view(),
         name='channel_course_list_edit'),

    path('channel/<slug:slug>/course_create/',
         CourseCreateView.as_view(),
         name='create_course'),

    path('channel/<slug:slug>/course_create_confirm/',
         CourseCreateFormHandle.as_view(),
         name='create_course_confirm'),

    path('course/<slug:slug>/',
         CourseDetail.as_view(),
         name='course'),

    path('course/<slug:slug>/update/',
         CourseUpdateView.as_view(),
         name='update_course'),

    path('course/<slug:slug>/update_description/',
         CourseDescriptionBlockUpdateView.as_view(),
         name='update_course_description'),
    #
    # path('channel_update_confirm/',
    #      ChannelUpdateView.as_view(),
    #      name='channel_update_confirm'),
]

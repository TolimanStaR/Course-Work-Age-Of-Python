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

    path('my_channel',
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

    path('course/<slug:slug>/students/',
         CourseStudentsListView.as_view(),
         name='course_students_list'),

    path('course/<slug:slug>/students/<str:username>/',
         CourseStudentDetailView.as_view(),
         name='course_student_detail'),

    path('course/<slug:slug>/join/',
         CourseJoinFormHandle.as_view(),
         name='join_course'),

    path('course/<slug:slug>/students/<str:username>/delete/',
         CourseDeleteStudentFormHandle.as_view(),
         name='course_delete_student'),

    path('course/<slug:slug>/module/create/',
         CourseModuleCreateView.as_view(),
         name='create_module'),

    path('course/<slug:slug>/module/create/success/',
         CourseModuleCreateFormHandle.as_view(),
         name='create_module_success'),

    path('course/<slug:slug>/module/<int:order>/update/',
         CourseModuleUpdate.as_view(),
         name='update_module'),

    path('course/<slug:slug>/modules/',
         CourseModuleList.as_view(),
         name='module_list'),

    path('course/<slug:slug>/module/<int:order>/content/<model_name>/create/',
         ContentCreateUpdateView.as_view(),
         name='course_module_content_create'),

    path('course/<slug:slug>/module/<int:order>/content/<model_name>/<id>/',
         ContentCreateUpdateView.as_view(),
         name='course_module_content_update'),

    path('course/<slug:slug>/module/<int:order>/content/list/',
         CourseModuleContentListView.as_view(),
         name='course_module_content_list'),

    path('course/<slug:slug>/module/<int:order>/delete_content/<id>/',
         ContentDeleteView.as_view(),
         name='course_module_content_delete'),

    path('course/<slug:slug>/task_list/',
         CourseTaskList.as_view(),
         name='course_task_list'),

    path('course/<slug:slug>/create_task/',
         CourseTaskCreateView.as_view(),
         name='course_task_create'),

    path('course/<slug:slug>/update_task/<id>/',
         CourseTaskUpdateView.as_view(),
         name='update_course_task'),

    path('course/<slug:slug>/create_task/confirm/',
         CourseTaskCreateFormHandle.as_view(),
         name='course_task_create_success'),

]

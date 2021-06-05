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

    path('course/<slug:slug>/module/<int:order>/content_create/<model_name>/',
         ContentCreateUpdateView.as_view(),
         name='course_module_content_create'),

    path('course/<slug:slug>/module/<int:order>/content/<model_name>/<int:id>/',
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

    path('course/<slug:slug>/task/<id>/tests/',
         CourseTaskTestView.as_view(),
         name='course_task_tests'),

    path('course/<slug:slug>/contest/list/',
         ContestListView.as_view(),
         name='contest_list_edit', ),

    path('course/<slug:slug>/contest/create/',
         ContestCreateView.as_view(),
         name='create_contest'),

    path('course/<slug:slug>/contest/create_success/',
         ContestCreateFormHandle.as_view(),
         name='create_contest_success', ),

    path('course/<slug:slug>/contest/<id>/update/',
         ContestUpdateView.as_view(),
         name='update_contest', ),

    path('course/<slug:slug>/contest/<id>/update_tasks/',
         ContestTaskListEditView.as_view(),
         name='contest_edit_tasks', ),

    path('course/<slug:slug>/contest/<id>/update_tasks_success/',
         ContestTaskListFormHandle.as_view(),
         name='contest_task_list_update_success', ),

    path('course/<slug:slug>/contest/<id>/edit_solutions/',
         ContestSolutionsListView.as_view(),
         name='contest_solutions_list', ),

    path('course/<slug:slug>/contest/<id>/edit_solution/<solution_id>/',
         ContestSolutionDetailView.as_view(),
         name='contest_solution_detail', ),

    path('course/<slug:slug>/contest/<id>/edit_solution/<solution_id>/rejudge/',
         ContestActionSolutionRejudgeFormHandle.as_view(),
         name='rejudge_contest_solution', ),

    path('course/<slug:slug>/contest/<id>/edit_solution/<solution_id>/delete_participant/',
         ContestActionDeleteParticipantFormHandle.as_view(),
         name='delete_contest_participant', ),

    path('contest/<id>/registration/',
         ContestParticipantRegistration.as_view(),
         name='contest_registration', ),

    path('contest/<id>/registration_success/',
         ContestParticipantRegistrationFormHandle.as_view(),
         name='contest_registration_success', ),

    path('contest/<id>/wait/',
         ContestParticipantWaitRoom.as_view(),
         name='contest_wait_room', ),

    path('contest/<id>/deleted/',
         ContestParticipantDeleteView.as_view(),
         name='contest_participant_deleted', ),

    # task list:

    path('contest/<id>/tasks/',
         ContestParticipantTaskListView.as_view(),
         name='contest_participant_task_list', ),

    # task detail:

    path('contest/<id>/task/<task_id>/',
         ContestParticipantTaskDetailView.as_view(),
         name='contest_participant_task_detail', ),

    # solution send:

    path('contest/<id>/send_solution/',
         ContestParticipantSendSolutionFileView.as_view(),
         name='contest_participant_send_solution', ),

    # solution send handle:

    path('contest/<id>/send_solution_success/',
         ContestParticipantSolutionSendSolutionFileFormHandle.as_view(),
         name='contest_participant_send_solution_success', ),

    # code send:

    path('contest/<id>/send_code/',
         ContestParticipantSendCodeView.as_view(),
         name='contest_participant_send_code', ),

    # code send handle:

    path('contest/<id>/send_code_success/',
         ContestParticipantSolutionSendCodeFormHandle.as_view(),
         name='contest_participant_send_code_success', ),

    # solution list:

    path('contest/<id>/solutions/',
         ContestParticipantSolutionListView.as_view(),
         name='contest_participant_solution_list', ),

    # solution detail:

    path('contest/<id>/solution/<solution_id>/',
         ContestParticipantSolutionDetailView.as_view(),
         name='contest_participant_solution_detail', ),

    # scoreboard:

    path('contest/<id>/scoreboard/',
         ContestParticipantScoreboardView.as_view(),
         name='contest_participant_scoreboard', ),

    path('contest/<id>/update_condition/',
         contest_condition_update_view,
         name='update_contest_condition', ),

    path('channel/<slug:slug>/course_list/',
         CourseListView.as_view(),
         name='course_list', ),

    path('course/<slug:slug>/module/<order>/',
         CourseModuleDetailView.as_view(),
         name='module', ),

    path('course/<slug:slug>/available_task_list/',
         CourseTaskListView.as_view(),
         name='course_student_task_list', ),

    path('course/<slug:slug>/task/<int:task_id>/',
         CourseTaskDetailView.as_view(),
         name='course_student_task_detail', ),

    path('course/<slug:slug>/task/<int:task_id>/send_solution/',
         CourseTaskSendSolutionFormHandle.as_view(),
         name='course_task_send_solution', ),

    path('course/<slug:slug>/task/<int:task_id>/solution/<int:solution_id>/',
         CourseSolutionDetailView.as_view(),
         name='course_solution_detail', ),

    path('course/<slug:slug>/contests/',
         ContestStudentListView.as_view(),
         name='contest_list', ),
]

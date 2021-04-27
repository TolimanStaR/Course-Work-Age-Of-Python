from django.urls import path

from . import views

urlpatterns = [
    path('list/',
         views.TaskList.as_view(),
         name='task_list'),

    path('task/<int:pk>/',
         views.TaskDetail.as_view(),
         name='task_detail'),

    path('task/<int:pk>/solutions/',
         views.SolutionList.as_view(),
         name='solution_list'),

    path('task/<int:pk>/solutions/<int:id>/',
         views.SolutionDetail.as_view(),
         name='solution_detail')

    ####
    ,
    path('task/<int:pk>/send/',
         views.TaskSolutionSend.as_view(),
         name='send'),
]

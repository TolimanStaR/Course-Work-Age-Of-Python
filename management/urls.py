from django.urls import path

from . import views

urlpatterns = [
    path('list/',
         views.AbstractTaskList.as_view(),
         name='abstract_task_view'),

    path('task/<pk>/',
         views.AbstractTaskDetail.as_view(),
         name='abstract_task_detail'),

    path('send_task/<pk>/',
         views.AbstractTaskForm.as_view(),
         name='abstract_task_form'),
]

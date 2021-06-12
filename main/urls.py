from django.urls import path
from .views import *

urlpatterns = [
    path('', MainPage.as_view(), name='main', ),
    path('politica/', Politica.as_view(), name='politica', ),
]

from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib import messages


class MainPage(TemplateView):
    template_name = 'main_page.html'

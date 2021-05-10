from django.shortcuts import render
from django.contrib.auth import views as auth_views
from django.views.generic import DetailView, TemplateView, FormView

from .models import UserProfile, User
from .forms import UserRegistrationForm


class Profile(DetailView):
    template_name = 'profile/profile.html'
    model = User
    context_object_name = 'user_obj'

    def get_object(self, queryset=None):
        return User.objects.get(username=self.kwargs['username'])


class UserRegister(TemplateView):
    template_name = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class UserRegisterFormHandle(FormView):
    form_class = UserRegistrationForm
    template_name = ''

    def form_valid(self, form):
        pass

    def get_success_url(self):
        pass

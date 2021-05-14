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
    template_name = 'registration/registration.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserRegistrationForm

        return context


class UserRegisterFormHandle(FormView):
    form_class = UserRegistrationForm
    template_name = 'registration/registration.html'

    def form_valid(self, form):
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
        return super().form_valid(form)

    def get_success_url(self):
        pass

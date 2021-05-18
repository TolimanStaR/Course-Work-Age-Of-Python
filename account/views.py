from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import views as auth_views
from django.urls import reverse
from django.views.generic import DetailView, TemplateView, FormView, ListView
from django.views.generic.base import TemplateResponseMixin
from django.views import View
from django.contrib import messages

from .models import UserProfile, User, FriendRequest
from .forms import UserRegistrationForm, UserEditForm, UserProfileEditForm, FriendRequestForm
from .forms import AcceptFriendRequestForm, DeclineFriendRequestForm, DeleteFriendForm


class UserList(ListView):
    template_name = 'profile/profile_list.html'
    model = User

    def get_queryset(self):
        return User.objects.all()


class Profile(DetailView):
    template_name = 'profile/profile.html'
    model = User
    context_object_name = 'user_obj'

    def get_object(self, queryset=None):
        return User.objects.get(username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['friends_list'] = self.object.user_profile.friends.all()
        context['friendship_request_form'] = FriendRequestForm
        context['accept_request_form'] = AcceptFriendRequestForm
        context['decline_request_form'] = DeclineFriendRequestForm
        context['remove_friend_form'] = DeleteFriendForm
        context['friendship_status'] = 'none'
        if self.request.user.is_authenticated:
            requests_from_current_user = FriendRequest.objects.filter(from_user=self.request.user.user_profile,
                                                                      to_user=self.object.user_profile)
            requests_to_current_user = FriendRequest.objects.filter(from_user=self.object.user_profile,
                                                                    to_user=self.request.user.user_profile)
            if self.request.user.user_profile in context['friends_list']:
                context['friendship_status'] = 'friend'
            else:
                if len(requests_from_current_user) == 0 and len(requests_to_current_user) == 0:
                    context['friendship_status'] = 'not friend'
                else:
                    if len(requests_to_current_user) > 0:
                        context['friendship_status'] = 'wait from'
                    elif len(requests_from_current_user) > 0:
                        context['friendship_status'] = 'wait to'
        return context


class GetUserInfoMixin(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_obj'] = User.objects.get(username=self.kwargs['username'])
        return context


class FriendRequestFormHandle(FormView, GetUserInfoMixin):
    template_name = 'profile/profile.html'
    form_class = FriendRequestForm

    def form_valid(self, form):
        new_request = FriendRequest.objects.create(
            from_user=self.request.user.user_profile,
            to_user=UserProfile.objects.get(user=User.objects.get(username=self.kwargs['username']))
        )
        new_request.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profile', kwargs=self.kwargs)


class AcceptFriendRequest(FormView, GetUserInfoMixin):
    template_name = 'profile_frame.html'
    form_class = AcceptFriendRequestForm

    # noinspection DuplicatedCode
    def form_valid(self, form):
        user_1 = UserProfile.objects.get(user=self.request.user)
        user_2 = UserProfile.objects.get(user=User.objects.get(username=self.kwargs['username']))
        from_friend_request = FriendRequest.objects.filter(from_user=user_1, to_user=user_1)
        to_friend_request = FriendRequest.objects.filter(from_user=user_2, to_user=user_1)
        from_friend_request.delete()
        to_friend_request.delete()
        user_1.friends.add(user_2)
        user_2.friends.add(user_1)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profile', kwargs=self.kwargs)


class DeclineFriendRequest(FormView, GetUserInfoMixin):
    template_name = 'profile_frame.html'
    form_class = DeclineFriendRequestForm

    # noinspection DuplicatedCode
    def form_valid(self, form):
        user_1 = UserProfile.objects.get(user=self.request.user)
        user_2 = UserProfile.objects.get(user=User.objects.get(username=self.kwargs['username']))
        from_friend_request = FriendRequest.objects.filter(from_user=user_1, to_user=user_2)
        to_friend_request = FriendRequest.objects.filter(from_user=user_2, to_user=user_1)
        print(from_friend_request, to_friend_request)
        from_friend_request.delete()
        to_friend_request.delete()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profile', kwargs=self.kwargs)


class RemoveFriend(FormView, GetUserInfoMixin):
    template_name = 'profile_frame.html'
    form_class = DeleteFriendForm

    def form_valid(self, form):
        user_1 = UserProfile.objects.get(user=self.request.user)
        user_2 = UserProfile.objects.get(user=User.objects.get(username=self.kwargs['username']))
        user_1.friends.remove(user_2)
        user_2.friends.remove(user_1)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profile', kwargs=self.kwargs)


class FriendList(ListView):
    template_name = 'profile/profile_friends_list.html'

    def get_queryset(self):
        user_profile = UserProfile.objects.get(user=User.objects.get(username=self.kwargs['username']))
        return user_profile.friends.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_obj'] = User.objects.get(username=self.kwargs['username'])
        return context


class FriendRequestList(ListView):
    template_name = 'profile/profile_friend_requests.html'
    model = FriendRequest

    def get_queryset(self):
        user_profile = UserProfile.objects.get(
            user=User.objects.get(username=self.kwargs['username']))
        return FriendRequest.objects.filter(to_user=user_profile)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = UserProfile.objects.get(
            user=User.objects.get(username=self.kwargs['username']))
        context['incoming_requests'] = FriendRequest.objects.filter(to_user=user_profile)
        context['user_obj'] = User.objects.get(username=self.kwargs['username'])
        return context


def friend_list_requests(request):
    if request.method == 'GET':
        pass

    if request.method == 'POST':
        pass


class EditProfile(View, LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))

        user_form = UserEditForm(instance=request.user)
        profile_form = UserProfileEditForm(instance=request.user.user_profile)
        return render(request, 'profile/profile_edit.html',
                      {'user_form': user_form,
                       'user_profile_form': profile_form,
                       'username': self.kwargs['username'],
                       'user_obj': request.user})

    def post(self, request, *args, **kwargs):
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = UserProfileEditForm(instance=request.user.user_profile,
                                           data=request.POST,
                                           files=request.FILES)
        if user_form.is_valid() & profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Данные обновлены')
        else:
            messages.error(request, 'Ошибка при обновлении профиля')
        return HttpResponseRedirect(self.request.path_info)


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
            new_profile = UserProfile.objects.create(
                user=new_user,
            )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('login', kwargs=self.kwargs)

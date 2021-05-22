from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DeleteView, FormView, DetailView, TemplateView, ListView
from django.contrib import messages

from .models import *

from .forms import *


class OwnerMixin(object):
    def __init__(self):
        self.request = None

    def get_queryset(self):
        qs = super(OwnerMixin, self).get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    def __init__(self):
        self.request = None

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)


class ChannelView(DetailView):
    model = Channel
    template_name = 'channel/channel.html'
    context_object_name = 'channel'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscribe_form'] = ChannelSubscribeForm
        context['delete_subscribe_form'] = ChannelDeleteSubscribeForm
        return context

    def get_object(self, queryset=None):
        if 'slug' in self.kwargs:
            return get_object_or_404(Channel, slug=self.kwargs['slug'])
        elif 'slug' not in self.kwargs and self.request.user.is_authenticated:
            return get_object_or_404(Channel, owner=self.request.user)

        raise Http404


class ChannelCreateView(TemplateView, LoginRequiredMixin):
    template_name = 'channel/channel_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channel_form'] = ChannelForm
        if self.request.user.is_authenticated:
            if hasattr(self.request.user, 'channel'):
                context['channel_form'] = ChannelForm(instance=Channel.objects.get(owner=self.request.user))
        return context


class ChannelCreateFormHandle(FormView, OwnerEditMixin):
    template_name = 'channel/channel_create.html'
    model = Channel
    form_class = ChannelForm

    def form_valid(self, form: forms.ModelForm):
        form.instance.owner = self.request.user
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('my_channel', kwargs=self.kwargs)


class ChannelUpdateView(UpdateView):
    model = Channel
    fields = ['title',
              'slug',
              'channel_description',
              'background_color',
              'preview_image',
              'background_image',
              'cover_image',
              'owner_full_name',
              'owner_interview',
              'owner_photo', ]
    template_name = 'channel/channel_update.html'

    def form_valid(self, form):
        return super().form_valid(form)

    def get_object(self, queryset=None):
        try:
            channel = Channel.objects.get(slug=self.kwargs['slug'])
            if channel.owner == self.request.user:
                return channel
            else:
                raise Http404
        except TypeError:
            raise Http404

    def get_success_url(self):
        messages.success(self.request, 'Настройки канала успешно обновлены')
        return self.request.path_info

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channel'] = get_object_or_404(Channel, slug=self.kwargs['slug'])
        return context


class ChannelSubscribersListView(ListView):
    template_name = 'channel/channel_subscribers_list.html'
    model = User

    def get_queryset(self):
        channel = get_object_or_404(Channel, slug=self.kwargs['slug'])
        return channel.subscribers.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channel'] = get_object_or_404(Channel, slug=self.kwargs['slug'])
        return context


class ChannelSubscriberDetailView(DetailView):
    template_name = 'channel/channel_subscriber_detail.html'
    model = User

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channel'] = get_object_or_404(Channel, slug=self.kwargs['slug'])
        return context


class ChannelSubscribeFormHandle(FormView):
    template_name = 'channel/channel.html'
    form_class = ChannelDeleteSubscribeForm

    def get_success_url(self):
        return reverse('channel', kwargs={'slug': self.kwargs['slug']})

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            raise Http404

        channel = get_object_or_404(Channel, slug=self.kwargs['slug'])
        channel.subscribers.add(self.request.user)
        channel.save()
        return super().form_valid(form)


class ChannelDeleteSubscribeFormHandle(FormView):
    template_name = 'channel/channel.html'
    form_class = ChannelDeleteSubscribeForm

    def get_success_url(self):
        kwargs = {'slug': self.kwargs['slug']}
        if self.request.user == Channel.objects.get(slug=self.kwargs['slug']).owner:
            return reverse('channel_subscribers', kwargs=kwargs)
        else:
            return reverse('channel', kwargs=kwargs)

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            raise Http404
        channel = get_object_or_404(Channel, slug=self.kwargs['slug'])
        if 'username' not in self.kwargs:
            channel.subscribers.remove(self.request.user)
        else:
            try:
                channel.subscribers.remove(get_object_or_404(User, username=self.kwargs['username']))
            except ObjectDoesNotExist:
                raise Http404
        channel.save()
        return super().form_valid(form)


class ManageChannelSubscriber(DetailView):
    template_name = 'channel/channel_subscriber_detail.html'
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channel'] = get_object_or_404(Channel, slug=self.kwargs['slug'])
        context['delete_subscriber_form'] = ChannelDeleteSubscribeForm
        return context

    def get_object(self, queryset=None):
        try:
            return get_object_or_404(User, username=self.kwargs['username'])
        except KeyError:
            raise Http404


class ChannelCoursesListView(ListView):
    pass


class ChannelDeleteView(DeleteView):
    pass

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DeleteView, FormView, DetailView, TemplateView
from django.contrib import messages

from .models import *

from .forms import ChannelForm


class OwnerMixin(object):
    def __init__(self):
        self.request = None

    def get_queryset(self):
        qs = super(OwnerMixin, self).get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    def __init__(self):
        self.request = None

    def form_valid(self):
        qs = super(OwnerEditMixin, self).form_valid()
        return qs.filter(owner=self.request.user)


class ChannelView(DetailView):
    model = Channel
    template_name = 'channel/channel.html'

    def get_object(self, queryset=None):
        print(self.kwargs)
        if 'slug' in self.kwargs:
            return get_object_or_404(Channel, slug=self.kwargs['slug'])
        elif 'slug' not in self.kwargs and self.request.user.is_authenticated:
            return get_object_or_404(Channel, owner=self.request.user)


class ChannelCreateView(TemplateView, LoginRequiredMixin):
    template_name = 'channel/channel_create.html'

    # model = Channel

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channel_form'] = ChannelForm
        return context


class ChannelCreateFormHandle(FormView):
    template_name = 'channel/channel_create.html'
    model = Channel

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('channel', kwargs=self.kwargs)


class ChannelUpdateView(UpdateView):
    pass


class ChannelUpdateFormHandle(FormView):
    pass


class ChannelDeleteView(DeleteView):
    pass

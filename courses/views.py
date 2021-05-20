from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DeleteView, FormView, DetailView, TemplateView, ListView
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

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)


class ChannelView(DetailView):
    model = Channel
    template_name = 'channel/channel.html'

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
    fields = ['title']
    template_name = 'channel/channel_update.html'

    def get_success_url(self):
        messages.success(self.request, 'Настройки канала успешно обновлены')
        return self.request.path_info


class ChannelSubscribersListView(ListView):
    pass


class ChannelSubscriberDetailView(DetailView):
    pass


class ChannelCoursesListView(ListView):
    pass


class ChannelDeleteView(DeleteView):
    pass

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, FormView, TemplateView

from .models import AbstractTask, Test, Solution, CodeFile
from .forms import SolutionForm


# This classes are used for testing only:

class TaskList(ListView):
    model = AbstractTask
    template_name = 'management/AbstractTaskList.html'


class TaskDetail(DetailView):
    model = AbstractTask
    template_name = 'management/AbstractTaskDetail.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SolutionForm
        return context


class TaskSolutionSend(FormView, LoginRequiredMixin):
    template_name = 'management/AbstractTaskDetail.html'
    form_class = SolutionForm

    def form_valid(self, form):
        code_file = CodeFile.objects.create(
            file=form.cleaned_data['file'],
            language=form.cleaned_data['language'],
            code=form.cleaned_data['file'].read().decode('utf-8'),
            file_name=form.cleaned_data['file'].name,
        )
        code_file.save()
        solution = Solution.objects.create(
            task=AbstractTask.objects.get(pk=self.kwargs['pk']),
            code_file=code_file,
            author=self.request.user,
        )
        solution.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('solution_list', kwargs=self.kwargs)


class SolutionList(ListView):
    model = Solution
    template_name = 'management/SolutionList.html'
    context_object_name = 'solutions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class SolutionDetail(DetailView):
    model = Solution
    template_name = 'management/SolutionDetail.html'
    context_object_name = 'solution'

    def get_object(self, queryset=None):
        return Solution.objects.get(pk=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['code'] = Solution.objects.get(pk=self.kwargs['id']).code_file.code
        return context

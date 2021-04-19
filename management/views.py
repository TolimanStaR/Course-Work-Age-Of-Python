from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, FormView, TemplateView

from .models import AbstractTask, Test, Solution, CodeFile
from .forms import SolutionForm


# This classes are used for testing only:

class AbstractTaskList(ListView):
    template_name = 'management/AbstractTaskList.html'
    model = AbstractTask

    queryset = AbstractTask.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AbstractTaskDetail(TemplateView):
    template_name = 'management/AbstractTaskDetail.html'

    def get_context_data(self, **kwargs):
        print(kwargs)
        context = super(AbstractTaskDetail, self).get_context_data(**kwargs)
        context['form'] = SolutionForm()
        context['task'] = AbstractTask.objects.get(pk=kwargs['pk'])
        return context


class AbstractTaskForm(FormView):
    form_class = SolutionForm

    success_url = 'management/list'

    def form_valid(self, form):
        code_file = CodeFile.objects.create(
            file=form.cleaned_data['file'],
            language=form.cleaned_data['language']
        )
        code_file.save()
        new_solution = Solution.objects.create(
            code_file=code_file,
            author=self.request.user,
        )
        new_solution.save()
        return super(AbstractTaskForm, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('abstract_task_view', args=())


class SolutionList(ListView):
    model = Solution
    context_object_name = 'solutions'
    template_name = 'management/SolutionList.html'

    def get_queryset(self):
        return Solution.objects.filter(author=self.request.user)

from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DeleteView, FormView, DetailView, TemplateView, ListView
from django.contrib import messages
from django.views.generic.base import View, TemplateResponseMixin
from django.forms.models import modelform_factory
from django.apps import apps
import uuid
from django.utils import timezone
from django.http import JsonResponse

from django.core.files import File

from .models import *
from management.models import CodeFile, SolutionEventType, Status, Verdict, lang_extension

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


class ChannelUpdateView(UpdateView, LoginRequiredMixin):
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


class ChannelSubscribersListView(ListView, LoginRequiredMixin):
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


class ManageChannelSubscriber(DetailView, LoginRequiredMixin):
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


class ChannelCoursesListView(ListView, LoginRequiredMixin):
    model = Course
    template_name = 'channel/channel_course_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channel'] = get_object_or_404(Channel, slug=self.kwargs['slug'])
        return context

    def get_queryset(self):
        # courses = Course.objects.all()
        # return courses.filter(owner=self.request.user,
        #                       channel=Channel.objects.get(slug=self.kwargs['slug']))

        channel = get_object_or_404(Channel, slug=self.kwargs['slug'])
        if channel.owner == self.request.user:
            qs = Course.objects.all()
            return qs.filter(owner=self.request.user)

        raise Http404


class CourseDetail(DetailView):  # Main page of the course
    model = Course
    template_name = 'course/course.html'
    context_object_name = 'course'

    def get_object(self, queryset=None):
        return get_object_or_404(Course, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['course_join_form'] = CourseJoinForm
        context['course_leave_form'] = CourseDeleteStudentForm
        context['is_subscribed'] = False

        obj = Course.objects.get(slug=self.kwargs.get('slug', None))
        if self.request.user.is_authenticated:
            sub_list = Student.objects.filter(
                course=obj,
                user=self.request.user,
            )
            if len(sub_list) > 0:
                context['is_subscribed'] = True

        return context


class CourseCreateView(TemplateView, LoginRequiredMixin):
    template_name = 'channel/channel_course_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['channel'] = get_object_or_404(Channel, slug=self.kwargs['slug'])
        context['course_create_form'] = CourseForm

        return context


class CourseCreateFormHandle(FormView, LoginRequiredMixin):
    template_name = 'channel/channel_course_create.html'
    form_class = CourseForm

    def form_valid(self, form):
        channel = get_object_or_404(Channel, slug=self.kwargs['slug'])
        if channel.owner == self.request.user:
            form.instance.owner = self.request.user
            form.instance.channel = channel
            if form.is_valid():
                form.save()
                messages.success(self.request, f'Курс {form.cleaned_data["title"]} успешно создан')
                return super().form_valid(form=form)

            messages.error(self.request, 'Ошибка при заполнении формы')

        raise Http404

    def get_success_url(self):
        return reverse('channel_course_list_edit', kwargs=self.kwargs)


class CourseUpdateView(UpdateView, LoginRequiredMixin):
    model = Course
    template_name = 'course/course_update.html'
    fields = (
        'title',
        'slug',
        'theme',
        'show_course_in_channel_page',
        'preview_picture',
        'main_picture',
    )

    def get_object(self, queryset=None):
        try:
            course = get_object_or_404(Course, slug=self.kwargs['slug'])
            if course.owner == self.request.user:
                return course
            raise Http404
        except TypeError:
            raise Http404

    def form_valid(self, form):
        messages.success(self.request, 'Данные о курсе успешно обновлены')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, slug=self.kwargs['slug'])
        return context

    def get_success_url(self):
        return self.request.path_info


class CourseDescriptionBlockUpdateView(TemplateView, TemplateResponseMixin, View):
    course = None
    template_name = 'course/course_update_description_blocks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, slug=self.kwargs['slug'])
        return context

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=self.kwargs['slug'])
        return super(CourseDescriptionBlockUpdateView, self).dispatch(request=request)

    def get_formset(self, *args):
        return CourseDescriptionBlockFormSet(
            *args,
            instance=self.course,
        )

    def get(self, request, *args, **kwargs):
        if self.request.user != Course.objects.get(slug=self.kwargs.get('slug', None)).owner:
            raise Http404
        formset = self.get_formset()
        return self.render_to_response({'course': self.course, 'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Данные успешно сохранены')
            return HttpResponseRedirect(reverse('update_course_description', kwargs={'slug': self.kwargs['slug']}))
        messages.error(request, 'Ошибка при сохранении данных')
        return self.render_to_response({'course': self.course, 'formset': formset})


class CourseStudentsListView(ListView):
    model = Student
    template_name = 'course/course_students_list.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user != Course.objects.get(slug=self.kwargs.get('slug', None)).owner:
            raise Http404
        return super(CourseStudentsListView, self).dispatch(request)

    def get_queryset(self):
        qs = Student.objects.all()
        return qs.filter(course=get_object_or_404(Course, slug=self.kwargs['slug']))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, slug=self.kwargs.get('slug'))
        return context


class CourseStudentDetailView(DetailView):
    model = Student
    template_name = 'course/course_student_detail.html'
    context_object_name = 'student'

    def get_object(self, queryset=None):
        return Student.objects.get(
            course=get_object_or_404(Course, slug=self.kwargs.get('slug', None)),
            user=get_object_or_404(User, username=self.kwargs.get('username', None))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, slug=self.kwargs.get('slug'))
        context['delete_student_form'] = CourseDeleteStudentForm
        return context


class CourseJoinFormHandle(FormView):
    form_class = CourseJoinForm
    template_name = 'course/course.html'

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            raise Http404
        course = get_object_or_404(Course, slug=self.kwargs.get('slug', None))
        user = self.request.user
        new_student = Student.objects.create(
            course=course,
            user=user,
            cur_module=1,
        )
        new_student.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('course', kwargs=self.kwargs)


class CourseDeleteStudentFormHandle(FormView):
    form_class = CourseDeleteStudentForm
    template_name = 'course/course_student_detail.html'

    def get_success_url(self):
        if self.request.user == Course.objects.get(slug=self.kwargs.get('slug', None)).owner:
            return reverse('course_students_list', kwargs={'slug': self.kwargs.get('slug', None)})
        else:
            return reverse('course', kwargs={'slug': self.kwargs.get('slug', None)})

    def form_valid(self, form):
        student = Student.objects.get(user=User.objects.get(username=self.kwargs.get('username', None)),
                                      course=Course.objects.get(slug=self.kwargs.get('slug', None)))
        student.delete()
        return super().form_valid(form)


class CourseModuleList(ListView):
    model = Module
    template_name = 'course/course_module_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(
            Course, slug=self.kwargs.get('slug', None)
        )
        return context

    def get_queryset(self):
        qs = Module.objects.filter(
            course=get_object_or_404(Course, slug=self.kwargs.get('slug', None))
        )
        return qs


class CourseModuleCreateView(TemplateView):
    template_name = 'course/course_module_create.html'

    def get_context_data(self, **kwargs):
        context = super(CourseModuleCreateView, self).get_context_data(**kwargs)
        context['course'] = get_object_or_404(
            Course, slug=self.kwargs.get('slug', None)
        )
        context['form'] = ModuleForm
        return context


class CourseModuleCreateFormHandle(FormView):
    template_name = 'course/course_module_create.html'
    form_class = ModuleForm

    def form_valid(self, form):
        if form.is_valid():
            course = Course.objects.get(slug=self.kwargs.get('slug', None))
            if self.request.user == course.owner:
                form.instance.owner = self.request.user
                form.instance.course = course
                form.save()
                messages.success(self.request, 'Модуль создан')
            else:
                raise Http404
        else:
            messages.error(self.request, 'Ошибка при создании модуля')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('module_list', kwargs=self.kwargs)


class CourseModuleUpdate(UpdateView):
    model = Module
    template_name = 'course/course_module_update.html'
    fields = (
        'title',
        'description',
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(
            Course, slug=self.kwargs.get('slug', None)
        )
        return context

    def get_object(self, queryset=None):
        return Module.objects.get(
            course=get_object_or_404(Course, slug=self.kwargs.get('slug', None)),
            order=self.kwargs.get('order', None)
        )

    def form_valid(self, form):
        messages.success(self.request, 'Данные о модуле успешно обновлены')
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path_info


class ContentCreateUpdateView(TemplateView, TemplateResponseMixin, View):
    course = None
    module = None
    model = None
    obj = None
    template_name = 'module/module_content_create_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = Course.objects.get(slug=self.kwargs['slug'])
        return context

    @staticmethod
    def get_model(model_name):
        if model_name in ['puretext',
                          # 'pdf',
                          'latex',
                          'codelisting',
                          'picture',
                          'videolink', ]:
            response = apps.get_model(app_label='courses', model_name=model_name)
            return response
        else:
            raise Http404

    @staticmethod
    def get_form(model, *args, **kwargs):
        form = modelform_factory(model=model,
                                 exclude=[
                                     'owner',
                                     'order',
                                     'created',
                                     'updated',
                                 ])
        return form(*args, **kwargs)

    def dispatch(self, request, slug, order, model_name, id=None, *args, **kwargs):
        self.course = Course.objects.get(slug=slug)
        self.module = get_object_or_404(Module, course=self.course, order=order)
        self.model = ContentCreateUpdateView.get_model(model_name)
        print(self.model.objects.all())
        if 'id' in self.kwargs:
            self.obj = self.model.objects.get(id=self.kwargs['id'] - 1)
        return super(ContentCreateUpdateView, self).dispatch(request, slug, order, model_name, id)

    def get(self, request, *args, **kwargs):
        form = ContentCreateUpdateView.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj, 'course': self.course})

    def post(self, request, slug, order, model_name, id=None, *args, **kwargs):
        form = ContentCreateUpdateView.get_form(self.model,
                                                instance=self.obj,
                                                data=request.POST,
                                                files=request.FILES)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = self.request.user
            obj.save()

            if not id:
                if self.model == LaTeX:
                    obj.text = obj.file.read().decode('utf-8')
                    obj.save()
                Content.objects.create(module=self.module, item=obj)

            return redirect('course_module_content_list', self.course.slug, self.module.order)

        return self.render_to_response({'form': form, 'object': self.obj, 'course': self.course})


class ContentDeleteView(View):
    def post(self, request, slug, order, id):
        content = get_object_or_404(
            Content,
            id=id,
            module__course__owner=self.request.user,
        )
        module = content.module
        course = module.course
        content.item.delete()
        content.delete()
        return redirect('course_module_content_list', course.slug, module.order)


class CourseModuleContentListView(TemplateView, LoginRequiredMixin):
    template_name = 'module/module_content_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(
            Course,
            slug=self.kwargs.get('slug', None)
        )
        if context['course'].owner != self.request.user:
            raise Http404
        context['module'] = get_object_or_404(
            Module,
            course=context['course'],
            order=self.kwargs.get('order', None)
        )
        qs = Content.objects.all()
        context['object_list'] = qs.filter(module=context['module'])
        return context


class CourseTaskList(ListView):
    model = CourseTask
    template_name = 'course/course_task_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = Course.objects.get(slug=self.kwargs.get('slug', None))
        return context

    def get_queryset(self):
        qs = self.model.objects.all()
        return qs.filter(course=Course.objects.get(slug=self.kwargs.get('slug', None)))


class CourseTaskCreateView(TemplateView):
    template_name = 'task/task_create.html'

    # noinspection DuplicatedCode
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = Course.objects.get(slug=self.kwargs.get('slug', None))
        context['course_task_form'] = CourseTaskForm
        return context


class CourseTaskCreateFormHandle(FormView):
    template_name = 'task/task_create.html'
    form_class = CourseTaskForm

    def form_valid(self, form):
        if form.is_valid():
            form.save(commit=False)
            form.instance.course = Course.objects.get(slug=self.kwargs.get('slug', None))
            new_code_file = CodeFile.objects.create(
                file=form.cleaned_data['solution_file_raw'],
                language=form.cleaned_data['solution_file_lang'],
                code=form.cleaned_data['solution_file_raw'].read().decode('utf-8'),
                file_name=form.cleaned_data['solution_file_raw'].name,
            )
            new_code_file.save()

            form.instance.solution_file = new_code_file
            form.save()
            task_validate_solution = CourseSolution.objects.create(
                author=self.request.user,
                code_file=new_code_file,
                task=form.instance,
                node=1,
                event_type=SolutionEventType.AUTHOR_TASK_VALIDATION,
                course=form.instance.course,
                course_task=form.instance,
            )
            task_validate_solution.save()
            form.instance.last_validate_solution = task_validate_solution
            form.save()
            messages.success(self.request, 'Задача сохранена')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('course_task_list', kwargs=self.kwargs)


class CourseTaskUpdateView(UpdateView):
    template_name = 'task/task_update.html'
    model = CourseTask
    fields = (
        'title',
        'task_description',
        'input_description',
        'output_description',
        'input_example',
        'output_example',
        'time_limit_seconds',
        'answer_type',
        'grading_system',
        'solution_file_raw',
        'solution_file_lang',
        'show_in_task_list',
        'difficulty',
    )

    def get_object(self, queryset=None):
        return get_object_or_404(CourseTask, id=self.kwargs.get('id', None))

    def form_valid(self, form):
        if form.is_valid():
            code_file = CodeFile.objects.get(task=form.instance)
            code_file.file = form.cleaned_data['solution_file_raw']
            code_file.language = form.cleaned_data['solution_file_lang']
            code_file.code = form.cleaned_data['solution_file_raw'].read().decode('utf-8')
            code_file.save()
            form.save()

            c_f = code_file
            c_f.pk = None
            c_f.save()

            task_validate_solution = CourseSolution.objects.create(
                author=self.request.user,
                code_file=c_f,
                task=form.instance,
                course=form.instance.course,
                course_task=form.instance,
                node=1,
                event_type=SolutionEventType.AUTHOR_TASK_VALIDATION,
            )
            task_validate_solution.save()

            form.instance.solution_file = code_file
            form.instance.last_validate_solution = task_validate_solution
            form.save()

            messages.success(self.request, 'Задача обновлена')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(
            Course, slug=self.kwargs.get('slug', None)
        )
        return context

    def get_success_url(self):
        return self.request.path_info


class CourseTaskTestView(TemplateView, TemplateResponseMixin, View):
    task = None
    course = None
    template_name = 'task/task_tests_create_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, slug=self.kwargs['slug'])
        context['task'] = get_object_or_404(CourseTask,
                                            id=self.kwargs.get('id', None))
        return context

    def dispatch(self, request, *args, **kwargs):
        self.task = get_object_or_404(CourseTask,
                                      id=self.kwargs.get('id', None))
        self.course = get_object_or_404(Course,
                                        slug=self.kwargs.get('slug', None))
        return super(CourseTaskTestView, self).dispatch(request=request)

    def get_formset(self, *args):
        formset = CourseTaskTestFormSet(
            *args,
            instance=self.task,
        )
        for form in formset:
            form.fields['content'].label = 'Содержимое теста:'
            form.fields['DELETE'].label = 'Удалить этот тест'

        return formset

    def get(self, request, *args, **kwargs):
        if self.request.user != Course.objects.get(slug=self.kwargs.get('slug', None)).owner:
            raise Http404
        formset = self.get_formset()
        return self.render_to_response({'course': self.course, 'task': self.task, 'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(request.POST, request.FILES)
        task = get_object_or_404(CourseTask, id=self.kwargs.get('id', None))
        for form in formset:
            form.instance.task = task
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Тесты сохранены')

            c_f = task.solution_file
            c_f.pk = None
            c_f.save()

            if len(formset) > 0:
                task_validate_solution = CourseSolution.objects.create(
                    author=self.request.user,
                    code_file=c_f,
                    course=task.course,
                    course_task=task,
                    task=task,
                    node=1,
                    event_type=SolutionEventType.AUTHOR_TASK_VALIDATION,
                )
                task_validate_solution.save()
                if task.last_validate_solution:
                    task.last_validate_solution = task_validate_solution
                else:
                    task.last_validate_solution = task_validate_solution
                task.save()

            return HttpResponseRedirect(reverse('course_task_tests', kwargs=self.kwargs))
        messages.error(request, 'Ошибка при сохранении тестов')
        return self.render_to_response({'course': self.course, 'task': self.task, 'formset': formset})


class ContestListView(ListView):
    template_name = 'contest/contest_list_edit.html'
    model = Contest

    def get_queryset(self):
        qs = Contest.objects.all()
        course = Course.objects.get(slug=self.kwargs['slug'])
        if course.owner != self.request.user:
            raise Http404
        return qs.filter(course=Course.objects.get(slug=self.kwargs['slug']))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContestForm
        context['course'] = get_object_or_404(
            Course, slug=self.kwargs.get('slug', None)
        )
        return context


class ContestCreateView(TemplateView, LoginRequiredMixin):
    template_name = 'contest/contest_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContestForm
        context['course'] = get_object_or_404(
            Course, slug=self.kwargs.get('slug', None)
        )
        return context


class ContestCreateFormHandle(FormView):
    form_class = ContestForm
    template_name = 'contest/contest_create.html'

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            raise Http404
        if form.is_valid():
            form.instance.course = get_object_or_404(
                Course, slug=self.kwargs.get('slug', None)
            )
            form.save()
            messages.success(self.request, 'Контест создан')
        else:
            messages.error(self.request, 'Произошла ошибка при создании контеста')
        return super(ContestCreateFormHandle, self).form_valid(form)

    def get_success_url(self):
        return reverse('contest_list_edit', kwargs=self.kwargs)


class ContestUpdateView(UpdateView, LoginRequiredMixin):
    model = Contest
    template_name = 'contest/contest_update.html'
    form_class = ContestForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(
            Course, slug=self.kwargs.get('slug', None)
        )
        return context

    def get_object(self, queryset=None):
        # course = Course.objects.get(self.kwargs['slug'])
        # if course.owner != self.request.user:
        #     raise Http404

        return get_object_or_404(
            Contest, id=self.kwargs.get('id', None)
        )

    def form_valid(self, form):
        if form.is_valid():
            form.save()
            messages.success(self.request, 'Контест успешно обновлен')
        else:
            messages.error(self.request, 'Произошла ошибка при обновлении контеста')
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.path_info


class ContestTaskListEditView(TemplateView, LoginRequiredMixin):
    template_name = 'contest/contest_task_choice.html'

    # noinspection DuplicatedCode
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            raise Http404
        context['contest'] = get_object_or_404(
            Contest, id=self.kwargs.get('id', None)
        )
        context['course'] = get_object_or_404(
            Course, slug=self.kwargs.get('slug', None)
        )
        context['form'] = ContestTaskChoiceForm(instance=Contest.objects.get(id=self.kwargs['id']))
        context['form'].fields['tasks'].queryset = CourseTask.objects.filter(
            course=context['course'],
        )
        return context


class ContestTaskListFormHandle(FormView):
    form_class = ContestTaskChoiceForm
    template_name = 'contest/contest_task_choice.html'

    def dispatch(self, request, *args, **kwargs):
        if request.POST.get('tasks') is None:
            messages.error(self.request, 'На соревновании дожна быть хотя бы одна задача!')
            return HttpResponseRedirect(reverse('contest_edit_tasks', kwargs=self.kwargs))
        return super().dispatch(request, **kwargs)

    def form_valid(self, form):
        contest = get_object_or_404(
            Contest,
            id=self.kwargs.get('id', None)
        )

        contest.tasks.remove(*contest.tasks.all())
        for task in form.cleaned_data['tasks']:
            contest.tasks.add(task)

        contest.save()
        messages.success(self.request, 'Список задач обновлен')
        return super(ContestTaskListFormHandle, self).form_valid(form)

    def get_success_url(self):
        return reverse('contest_edit_tasks', kwargs=self.kwargs)


class ContestSolutionsListView(ListView):
    model = ContestSolution
    template_name = 'contest/contest_solutions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            raise Http404
        context['course'] = get_object_or_404(
            Course, slug=self.kwargs.get('slug', None)
        )
        context['contest'] = get_object_or_404(
            Contest, id=self.kwargs.get('id', None)
        )
        return context

    def get_queryset(self):
        qs = ContestSolution.objects.all()
        contest = get_object_or_404(
            Contest,
            id=self.kwargs.get('id', None)
        )
        return qs.filter(participant__contest=contest)


class ContestSolutionDetailView(DetailView):
    model = ContestSolution
    template_name = 'contest/contest_solution_detail.html'
    context_object_name = 'solution'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            raise Http404
        context['contest'] = get_object_or_404(
            Contest, id=self.kwargs.get('id', None)
        )
        context['course'] = get_object_or_404(
            Course, slug=self.kwargs.get('slug', None)
        )

        context['action_rejudge_form'] = ContestActionSolutionRejudge
        context['action_delete_participant_form'] = ContestActionDeleteParticipant
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(
            ContestSolution,
            id=self.kwargs.get('solution_id', None)
        )


class ContestActionSolutionRejudgeFormHandle(FormView):
    template_name = 'contest/contest_solution_detail.html'
    form_class = ContestActionSolutionRejudge

    def form_valid(self, form):
        messages.success(self.request, 'Решение было отправлено на перепроверку')
        solution = get_object_or_404(
            ContestSolution,
            id=self.kwargs.get('solution_id', None)
        )
        solution.status = Status.WAIT_FOR_CHECK
        solution.verdict = Verdict.EMPTY_VERDICT
        solution.verdict_text = 'Посылка не проверена'
        solution.save()
        return super().form_valid(form=form)

    def get_success_url(self):
        return reverse('contest_solution_detail', kwargs=self.kwargs)


class ContestActionDeleteParticipantFormHandle(FormView):
    template_name = 'contest/contest_solution_detail.html'
    form_class = ContestActionDeleteParticipant

    def form_valid(self, form):
        reason = form.cleaned_data['reason']
        solution = get_object_or_404(
            ContestSolution,
            id=self.kwargs.get('solution_id', None)
        )
        solution.participant.deleted = True
        solution.participant.delete_reason = reason
        solution.participant.save()
        return super().form_valid(form=form)

    def get_success_url(self):
        return reverse('contest_solutions_list', kwargs={
            'slug': self.kwargs['slug'],
            'id': self.kwargs['id'],
        })


class ContestParticipantRegistration(TemplateView):
    template_name = 'contest/contest_participant_registration.html'

    def dispatch(self, request, *args, **kwargs):
        contest = Contest.objects.get(id=self.kwargs.get('id', None))
        if self.request.user.is_authenticated:

            if ContestParticipant.objects.filter(
                    user=self.request.user,
                    contest=Contest.objects.get(id=self.kwargs.get('id', None))
            ).count() > 0:
                if contest.status == ContestStatus.WAIT_FOR_START:
                    return HttpResponseRedirect(
                        reverse('contest_wait_room', kwargs=self.kwargs)
                    )
                else:
                    return HttpResponseRedirect(
                        reverse('contest_participant_task_list', kwargs=self.kwargs)
                    )

        return super(ContestParticipantRegistration, self).dispatch(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contest'] = get_object_or_404(
            Contest, id=self.kwargs.get('id', None)
        )
        context['form'] = ContestParticipantRegistrationForm
        context['already_participant'] = False

        if self.request.user.is_authenticated:
            if ContestParticipant.objects.filter(
                    contest=context['contest'],
                    user=self.request.user,
            ).count() > 0:
                context['already_participant'] = True
        return context


class ContestParticipantRegistrationFormHandle(FormView):
    form_class = ContestParticipantRegistrationForm
    template_name = 'contest/contest_participant_registration.html'

    def form_valid(self, form):
        participant = ContestParticipant.objects.create(
            contest=Contest.objects.get(id=self.kwargs['id'], ),
            user=self.request.user,
        )
        participant.save()
        return super().form_valid(form=form)

    def get_success_url(self):
        return reverse('contest_participant_task_list', kwargs=self.kwargs)


class ContestParticipantMixin(TemplateView):
    object_list = None
    # object = None
    template_name = ''

    def dispatch(self, request, *args, **kwargs):
        try:
            if self.get_participant().deleted:
                return HttpResponseRedirect(
                    reverse('contest_participant_deleted', kwargs=self.kwargs)
                )
        except ObjectDoesNotExist:
            pass
        # if self.get_contest().status == ContestStatus.WAIT_FOR_START:
        #     if self.request.path_info != reverse('contest_wait_room', kwargs=self.kwargs):
        #         return HttpResponseRedirect(
        #             reverse('contest_wait_room', kwargs=self.kwargs)
        #         )
        return super().dispatch(request=request, **kwargs)

    def get_contest(self):
        return get_object_or_404(
            Contest, id=self.kwargs.get('id', None)
        )

    def get_contest_status(self):
        return self.get_contest().status

    def get_participant(self):
        return ContestParticipant.objects.get(
            contest=self.get_contest(),
            user=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contest'] = self.get_contest()
        try:
            context['participant'] = self.get_participant()
        except ObjectDoesNotExist:
            context['participant'] = None
        return context


class ContestParticipantWaitRoom(ContestParticipantMixin):
    template_name = 'contest/contest_participant_wait_room.html'


class ContestParticipantTaskListView(ListView, ContestParticipantMixin):
    model = CourseTask
    template_name = 'contest/contest_participant_task_list.html'

    def get_queryset(self):
        return self.get_contest().tasks.all()


class ContestParticipantTaskDetailView(DetailView, ContestParticipantMixin):
    model = CourseTask
    template_name = 'contest/contest_participant_task_detail.html'
    context_object_name = 'task'

    def get_object(self, queryset=None):
        return get_object_or_404(
            CourseTask,
            id=self.kwargs.get('task_id', None)
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)


class ContestParticipantSendSolutionFileView(ContestParticipantMixin):
    template_name = 'contest/contest_participant_send_solution.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContestSolutionSendSolutionForm
        # print(dir(context['form']))
        # print(dir(context['form'].declared_fields['task']))
        context['form'].declared_fields['task'].queryset = self.get_contest().tasks.all()
        # context['form'].fields['task'].queryset = self.get_contest().tasks.all()
        return context


class ContestParticipantSendCodeView(ContestParticipantMixin):
    template_name = 'contest/contest_participant_send_code.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContestSolutionSendCodeForm
        context['form'].declared_fields['task'].queryset = self.get_contest().tasks.all()
        return context


class ContestParticipantSolutionSendSolutionFileFormHandle(FormView, ContestParticipantMixin):
    template_name = 'contest/contest_participant_send_solution.html'
    form_class = ContestSolutionSendSolutionForm

    # noinspection DuplicatedCode
    def form_valid(self, form):
        if form.is_valid():
            code_file = CodeFile.objects.create(
                file=form.cleaned_data['file'],
                language=form.cleaned_data['language'],
                code=form.cleaned_data['file'].read().decode('utf-8'),
                file_name=form.cleaned_data['file'].name,
            )
            code_file.save()
            solution = ContestSolution.objects.create(
                participant=self.get_participant(),
                author=self.get_participant().user,
                code_file=code_file,
                task=form.cleaned_data['task'],
            )
            solution.save()
            self.get_participant().penalty += (datetime.datetime.now(
                datetime.timezone.utc) - self.get_contest().start_time).seconds // 60
            self.get_participant().save()
            messages.success(self.request, 'Ваше решение отправлено на проверку')
        else:
            messages.error(self.request, 'При отправке решения произошла ошибка')

        return super(ContestParticipantSolutionSendSolutionFileFormHandle, self).form_valid(form=form)

    def get_success_url(self):
        return reverse('contest_participant_solution_list', kwargs=self.kwargs)


class ContestParticipantSolutionSendCodeFormHandle(FormView, ContestParticipantMixin):
    template_name = 'contest/contest_participant_send_code.html'
    form_class = ContestSolutionSendCodeForm

    # noinspection DuplicatedCode
    def form_valid(self, form):
        if form.is_valid():
            file_name = f'{str(uuid.uuid4())}.{lang_extension[form.cleaned_data["language"]]}'
            file = open(f'media/raw_code/{file_name}', 'w')
            file.write(form.cleaned_data['code'])
            file.close()
            f = File(file=file)
            f.open('r')
            code_file = CodeFile.objects.create(
                file=f,
                language=form.cleaned_data['language'],
                code=form.cleaned_data['code'],
                file_name=file_name,
            )
            f.close()
            code_file.save()
            solution = ContestSolution.objects.create(
                participant=self.get_participant(),
                author=self.get_participant().user,
                code_file=code_file,
                task=form.cleaned_data['task'],
            )
            solution.save()
            self.get_participant().penalty += (datetime.datetime.now(
                datetime.timezone.utc) - self.get_contest().start_time).seconds // 60
            self.get_participant().save()
            messages.success(self.request, 'Ваш код отправлен на проверку')
        else:
            messages.error(self.request, 'При отправке кода произошла ошибка')
        return super(ContestParticipantSolutionSendCodeFormHandle, self).form_valid(form=form)

    def get_success_url(self):
        return reverse('contest_participant_solution_list', kwargs=self.kwargs)


class ContestParticipantSolutionListView(ListView, ContestParticipantMixin):
    model = ContestSolution
    template_name = 'contest/contest_participant_solution_list.html'

    def get_queryset(self):
        qs = ContestSolution.objects.all()
        print(qs)
        return qs.filter(
            participant=self.get_participant(),
            participant__contest=self.get_contest(),
        )

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return super().get(request, *args, **kwargs)


class ContestParticipantSolutionDetailView(DetailView, ContestParticipantMixin):
    model = ContestSolution
    template_name = 'contest/contest_participant_solution_detail.html'
    context_object_name = 'solution'

    def get_object(self, queryset=None):
        return get_object_or_404(
            ContestSolution,
            id=self.kwargs.get('solution_id', None),
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)


class ContestParticipantScoreboardView(ContestParticipantMixin):
    template_name = 'contest/contest_participant_scoreboard.html'

    class TableElement:
        def __init__(self):
            self.is_solved = None
            self.try_count = None
            self.points = None

    class User:
        def __init__(self):
            self.username = None
            self.stats: ContestParticipantScoreboardView.TableElement = None
            self.task_solved = None
            self.points = 0
            self.type = 0

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        participants = ContestParticipant.objects.filter(
            contest=self.get_contest(),
        )
        tasks = self.get_contest().tasks.all()
        context['tasks'] = tasks
        table = []
        for participant in participants:
            user = self.User()
            user.username = participant.user.username
            stats = [self.TableElement() for _ in range(len(tasks))]
            solved_cnt = 0
            points = 0
            for i in range(len(tasks)):
                solutions = ContestSolution.objects.filter(
                    participant=participant,
                    task=tasks[i],
                )
                stats[i].try_count = len(solutions)
                stats[i].points = max([s.points for s in solutions] + [-1])
                points += stats[i].points
                stats[i].is_solved = True if Verdict.CORRECT_SOLUTION in [s.verdict for s in solutions] else False
                if stats[i].is_solved:
                    solved_cnt += 1
            user.stats = stats
            user.task_solved = solved_cnt
            user.points = points
            if context['contest'].status == ContestStatus.FINISHED:
                user.type = 1
            table.append(user)
        table.sort(key=lambda x: x.task_solved, reverse=True)
        context['table'] = table
        return context


class ContestParticipantDeleteView(TemplateView):
    template_name = 'contest/contest_participant_deleted.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['participant'] = ContestParticipant.objects.get(
            contest=Contest.objects.get(id=self.kwargs['id']),
            user=self.request.user,
        )
        return context


def contest_condition_update_view(request, id):
    contest = Contest.objects.get(id=id)
    now_time = timezone.now() + datetime.timedelta(hours=3)
    start = contest.start_time + datetime.timedelta(hours=3)
    finish = contest.start_time + contest.duration + datetime.timedelta(hours=3)
    data = {
        'contest_status': 'wait_for_start',
        'alert_action': 0,
        'alert_message': None,
        'timer': None,
    }
    if now_time < start:
        if contest.status == ContestStatus.WAIT_FOR_START:
            pass
        else:
            contest.status = ContestStatus.WAIT_FOR_START
    if start <= now_time <= finish:
        if contest.status == ContestStatus.ACTIVE:
            pass
        else:
            contest.status = ContestStatus.ACTIVE
            data['contest_status'] = 'active'
            data['alert_action'] = 1
            data['alert_message'] = 'Соревнование началось'
            data['timer'] = str(now_time - start)

    if finish < now_time:
        if contest.status == ContestStatus.FINISHED:
            pass
        else:
            contest.status = ContestStatus.FINISHED
            data['contest_status'] = 'finished'
            data['alert_action'] = 2
            data['alert_message'] = 'Соревнование закончилось'
            data['timer'] = 'Время истекло'

    contest.save()
    return JsonResponse(data, status=200)


# Here starts views which are handle user's interface requests


class CourseListView(ListView):
    model = Course
    template_name = 'course/course_student_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channel'] = get_object_or_404(
            Channel,
            slug=self.kwargs.get('slug', None),
        )
        return context

    def get_queryset(self):
        qs = Course.objects.all()
        channel = get_object_or_404(
            Channel,
            slug=self.kwargs.get('slug', None),
        )
        return qs.filter(channel=channel)


class CourseModuleDetailView(DetailView):
    model = Module
    template_name = 'module/module.html'
    context_object_name = 'module'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(
            Course,
            slug=self.kwargs.get('slug', None)
        )
        m = get_object_or_404(
            Module,
            course=context['course'],
            order=self.kwargs.get('order', None),
        )
        context['prev_module'] = None if Module.objects.filter(course=
                                                               context['course'],
                                                               order=
                                                               m.order - 1).count() == 0 else Module.objects.get(
            course=
            context['course'], order=m.order - 1)
        context['next_module'] = None if Module.objects.filter(course=
                                                               context['course'],
                                                               order=
                                                               m.order + 1).count() == 0 else Module.objects.get(
            course=
            context['course'], order=m.order + 1)
        return context

    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug', None)
        order = self.kwargs.get('order', None)
        return get_object_or_404(
            Module,
            course=Course.objects.get(slug=slug),
            order=order,
        )


class CourseTaskListView: pass


class CourseTaskDetailView: pass


class CourseSolutionDetailView: pass


class CourseTaskSendSolutionFormHandle: pass

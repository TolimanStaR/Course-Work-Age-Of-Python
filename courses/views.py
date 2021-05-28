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

from .models import *
from management.models import CodeFile

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
            return apps.get_model(app_label='courses', model_name=model_name)
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
        if id:
            self.obj = get_object_or_404(
                self.model,
                id=id,
                owner=self.request.user,
            )
        return super(ContentCreateUpdateView, self).dispatch(request, slug, order, model_name)

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
            # add solution creation to send to validate it
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

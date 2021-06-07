from django import forms
from django.forms.models import inlineformset_factory
from datetimewidget.widgets import DateTimeWidget, TimeWidget

from .models import *


class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = (
            'title',
            'slug',
            'channel_description',
            'background_color',
            'preview_image',
            'background_image',
            'cover_image',
            'owner_full_name',
            'owner_interview',
            'owner_photo',
        )


class ChannelSubscribeForm(forms.Form):
    pass


class ChannelDeleteSubscribeForm(forms.Form):
    pass


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = (
            'title',
            'slug',
            'description',
            'theme',
            'show_course_in_channel_page',
            'preview_picture',
            'main_picture',
        )


CourseDescriptionBlockFormSet = inlineformset_factory(
    parent_model=Course,
    model=CourseDescriptionBlock,
    fields=('title',
            'subtitle',
            'text',
            'image',
            'image_position',),
    extra=1,
    can_order=True,
    can_delete=True,
)

CourseTaskTestFormSet = inlineformset_factory(
    parent_model=CourseTask,
    model=Test,
    fields=(
        'content',
    ),
    extra=3,
    can_delete=True,
)


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = (
            'title',
            'description',
        )


class CourseJoinForm(forms.Form):
    pass


class CourseDeleteStudentForm(forms.Form):
    pass


class CourseTaskForm(forms.ModelForm):
    class Meta:
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


class ContestForm(forms.ModelForm):
    class Meta:
        model = Contest
        fields = (
            'title',
            'start_time',
            'duration',
        )
        widgets = {
            'start_time': DateTimeWidget(attrs={'id': 'start_time'}, usel10n=True, bootstrap_version=3),
            'duration': None
        }


class ContestTasksForm(forms.Form):
    tasks = forms.ModelMultipleChoiceField(queryset=AbstractTask.objects.all(), widget=forms.CheckboxSelectMultiple)


class ContestTaskChoiceForm(forms.ModelForm):
    class Meta:
        model = Contest
        fields = (
            'tasks',
        )

    tasks = forms.ModelMultipleChoiceField(
        queryset=CourseTask.objects.all(),
        widget=forms.CheckboxSelectMultiple,

    )


class ContestActionSolutionRejudge(forms.Form):
    pass


class ContestActionDeleteParticipant(forms.Form):
    reason = forms.CharField()


class ContestParticipantRegistrationForm(forms.Form):
    pass


class ContestSolutionSendSolutionForm(forms.Form):
    task = forms.ModelChoiceField(queryset=CourseTask.objects.all())
    language = forms.ChoiceField(choices=Language.choices)
    file = forms.FileField()


class ContestSolutionSendCodeForm(forms.Form):
    task = forms.ModelChoiceField(queryset=CourseTask.objects.all())
    language = forms.ChoiceField(choices=Language.choices)
    code = forms.CharField(widget=forms.Textarea)


class CourseTaskSendSolutionForm(forms.Form):
    language = forms.ChoiceField(choices=Language.choices, label='Язык программирования')
    file = forms.FileField(required=False, label='Файл с кодом')
    code = forms.CharField(widget=forms.Textarea, required=False, label='Код')

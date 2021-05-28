from django import forms
from django.forms.models import inlineformset_factory

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
        )

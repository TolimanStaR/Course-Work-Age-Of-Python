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
    fields=['title',
            'subtitle',
            'text',
            'image',
            'image_position'],
    extra=2,
    can_order=True,
    can_delete=True,
)

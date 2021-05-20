from django import forms

from .models import Channel


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

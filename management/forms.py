from django import forms

from .models import Language


class SolutionForm(forms.Form):
    file = forms.FileField()
    language = forms.ChoiceField(choices=Language.choices)

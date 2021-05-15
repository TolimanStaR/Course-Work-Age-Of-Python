from django import forms
from .models import User, UserProfile, FriendRequest


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Введите пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Пароли не совпадают')
        return cd['password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
        )


class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = (
            'status',
            'profile_photo',
            'profile_background'
        )


class FriendRequestForm(forms.Form):
    pass


class AcceptFriendRequestForm(forms.Form):
    pass


class DeclineFriendRequestForm(forms.Form):
    pass


class DeleteFriendForm(forms.Form):
    pass

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.utils.translation import gettext, gettext_lazy as _
from django_countries.data import COUNTRIES
from django_countries.widgets import CountrySelectWidget
from django.contrib.auth import get_user_model
# from django.forms import ModelChoiceField
from .models import Profile


class ProfileForm(forms.ModelForm):
    # country = forms.CharField(label='', required=False, widget=CountrySelectWidget({}))

    bio = forms.CharField(label='', required=False, widget=forms.Textarea(attrs={
        'placeholder': 'المواصفات الشخصية', 'class': 'forms',
        "cols": 10,
        "rows": 2,
    }))
    website = forms.CharField(label='', required=False,  widget=forms.TextInput(attrs={
        'placeholder': 'موقع إلكتوني', 'class': 'forms'
    }))

    class Meta:
        model = Profile
        fields = 'country',  'bio', 'photo', 'website'
        widgets = {'country': CountrySelectWidget()}


class UserForm(forms.ModelForm):
    username = forms.CharField(label='', widget=forms.TextInput(
        attrs={"placeholder": 'اسم المستخدم', 'class': 'forms'}))
    email = forms.EmailField(label='', widget=forms.EmailInput(
        attrs={"placeholder": 'عنوان بريد إلكتروني', 'class': 'forms'}))
    first_name = forms.CharField(label='', widget=forms.TextInput(
        attrs={"placeholder": 'الاسم الأول', 'class': 'forms'}), required=False)
    last_name = forms.CharField(label='', widget=forms.TextInput(
        attrs={"placeholder": 'الاسم الأخير', 'class': 'forms'}), required=False)

    class Meta:
        model = User
        fields = 'username', 'email', 'first_name', 'last_name'


class UserSignupForm(UserCreationForm):
    username = forms.CharField(label='', widget=forms.TextInput(
        attrs={"placeholder": 'اسم المستخدم', 'class': 'forms'}))
    password1 = forms.CharField(
        label='', widget=forms.PasswordInput(attrs={"placeholder": 'كلمة المرور', 'class': 'forms'}))
    password2 = forms.CharField(
        label='', widget=forms.PasswordInput(attrs={"placeholder": 'تأكيد كلمة المرور', 'class': 'forms'}))
    email = forms.EmailField(label='', widget=forms.EmailInput(
        attrs={"placeholder": 'عنوان بريد إلكتروني', 'class': 'forms'}))

    class Meta:
        model = User
        fields = 'username', 'email', 'password1', 'password2'

    def clean_email(self):
        email = self.cleaned_data.get("email")
        obj = get_user_model().objects.filter(email=email)
        if obj == None:
            raise forms.ValidationError("this email already exist")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2


class LoginForm(forms.Form):
    email_or_username = forms.CharField(label='', widget=forms.TextInput(
        attrs={"placeholder": ' اسم المستخدم او البريد الإلكتروني ', 'class': 'forms'}))
    password = forms.CharField(
        label='', widget=forms.PasswordInput(attrs={"placeholder": 'كلمة المرور', 'class': 'forms'}))


class ChangeUserPasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=_(""),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'current-password', 'autofocus': True, "placeholder": "كلمة المرور القديمة", 'class': 'forms'}),
    )
    new_password1 = forms.CharField(
        label=_(""),
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', "placeholder": "كلمة المرور الجديدة", 'class': 'forms'}),
        strip=False
    )
    new_password2 = forms.CharField(
        label=_(""),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', "placeholder": "تأكيد كلمة المرور الجديدة", 'class': 'forms'}),
    )


class ResetPasswordForm(forms.Form):
    email_or_username = forms.CharField(label='', widget=forms.TextInput(
        attrs={"placeholder": ' اسم المستخدم او البريد الإلكتروني ', 'class': 'forms'}))


class CheckCodeForm(forms.Form):
    code = forms.IntegerField(label='', widget=forms.TextInput(attrs={
        'class': 'forms',
        'placeholder': 'ادخل رقم التأكيد'
    }))


class ChangePasswordResetForm(forms.Form):
    password1 = forms.CharField(
        label=_(""),
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', "placeholder": "كلمة المرور الجديدة", 'class': 'forms'}),
        strip=False
    )
    password2 = forms.CharField(
        label=_(""),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', "placeholder": "تأكيد كلمة المرور الجديدة", 'class': 'forms'}),
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('.كلمة السر غير متشبها')
        if len(password2) < 8:
            raise forms.ValidationError(
                'كلمة المرور هذه قصيرة جدا. يجب أن تتكون من 8 حروف على الأقل.')
        return password2

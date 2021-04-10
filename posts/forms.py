from django import forms
from .models import Article, Tag, Comment


class ArticleForm(forms.ModelForm):
    title = forms.CharField(label='', widget=forms.TextInput(
        attrs={'placeholder': 'العنوان', 'class': 'forms'}))
    sub_title = forms.CharField(label='', widget=forms.Textarea(
        attrs={'placeholder': 'العنوان الفرعي', 'cols': 40, 'rows': 5, 'class': 'forms'}))
    # body = forms.CharField(label='', widget=forms.Textarea(
    #     attrs={'placeholder': 'المقال', 'class': 'forms'}))

    class Meta:
        model = Article
        fields = 'title', 'sub_title', 'body', 'status',  'picture'
        widgets = {
            'status': forms.RadioSelect
        }


class TagForm(forms.ModelForm):
    tag = forms.CharField(label='', required=False, widget=forms.TextInput(
        attrs={'placeholder': 'Tag',  'class': 'forms'}))

    class Meta:
        model = Tag
        fields = 'tag',


class CommentForm(forms.Form):
    comment = forms.CharField(label='', required=False, widget=forms.TextInput(
        attrs={'placeholder': 'أدخل تعليقك هنا... ', 'class': 'forms', 'aautocomplte': False}))

    # class Meta:
    #     model = Comment
    #     fields = 'comment',

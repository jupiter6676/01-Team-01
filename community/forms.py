from django import forms
from .models import *
from django.forms import ClearableFileInput

class ArticlesForm(forms.ModelForm):
    class Meta:
        model = Articles
        fields = [
            "title",
            "content",
        ]
        labels = {
            "title": "제목",
            "content": "내용",
        }

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ("image",)
        widgets = {
            "image": ClearableFileInput(attrs={"multiple": True}),
        }

class CommentsForm(forms.ModelForm):
    content = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={
            "placeholder": "댓글을 작성해주세요.",
        })
    )
    class Meta:
        model = Comments
        fields = ['content',]
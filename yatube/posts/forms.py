from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = {
            'group': 'Group',
            'text': 'Text',
        }
        help_texts = {
            'group': 'Choose a group from the list',
            'text': 'Some text',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Text',
        }
        help_texts = {
            'text': 'Some text',
        }

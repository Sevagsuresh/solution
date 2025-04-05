from django import forms # type: ignore
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Comment
from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'youtube_url', 'image', 'video_file']
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': 'Enter post content',
                'rows': 3
            }),
            'youtube_url': forms.URLInput(attrs={
                'placeholder': 'Enter YouTube URL'
            })
        }


class CustomRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']  # Use password1 and password2 for UserCreationForm validation

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'youtube_url', 'image', 'video_file']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Add a comment...'}),
        }
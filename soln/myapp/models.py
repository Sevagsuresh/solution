from django import forms
from django.contrib.auth.models import User

class CustomRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='posts/images/', blank=True, null=True)
    video_file = models.FileField(upload_to='posts/videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_embed_url(self):
        if self.youtube_url:
            return self.youtube_url.replace('watch?v=', 'embed/').replace('youtu.be/', 'youtube.com/embed/')
        return None

    def __str__(self):
        return f"Post by {self.user.username} - {self.created_at}"
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    reply = models.TextField(blank=True, null=True)  # Admin reply

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post}"

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"Like by {self.user.username} on {self.post}"
    
class Dislike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='dislikes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"Dislike by {self.user.username} on {self.post}"

class OxygenAvailability(models.Model):
    DISTRICT_CHOICES = [
        ('Thiruvananthapuram', 'Thiruvananthapuram'),
        ('Kollam', 'Kollam'),
        ('Pathanamthitta', 'Pathanamthitta'),
        ('Alappuzha', 'Alappuzha'),
        ('Kottayam', 'Kottayam'),
        ('Idukki', 'Idukki'),
        ('Ernakulam', 'Ernakulam'),
        ('Thrissur', 'Thrissur'),
        ('Palakkad', 'Palakkad'),
        ('Malappuram', 'Malappuram'),
        ('Kozhikode', 'Kozhikode'),
        ('Wayanad', 'Wayanad'),
        ('Kannur', 'Kannur'),
        ('Kasaragod', 'Kasaragod'),
    ]
    district = models.CharField(max_length=100, choices=DISTRICT_CHOICES, unique=True)
    availability_percent = models.DecimalField(max_digits=5, decimal_places=2)
    capacity_mt = models.DecimalField(max_digits=10, decimal_places=2)
    demand_mt_per_day = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.district

# models.py

from django.db import models

class SafeAwarePoll(models.Model):
    title = models.CharField(max_length=200)  # e.g., Nipah Virus Safety Poll
    question = models.TextField()  # e.g., Are you safe?
    created_at = models.DateTimeField(auto_now_add=True)

class SafeAwareResponse(models.Model):
    poll = models.ForeignKey(SafeAwarePoll, on_delete=models.CASCADE)
    district = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    is_safe = models.BooleanField()  # True for Yes, False for No
    submitted_at = models.DateTimeField(auto_now_add=True)

class NormalPoll(models.Model):
    question = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class NormalPollResponse(models.Model):
    poll = models.ForeignKey(NormalPoll, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    response = models.CharField(choices=[('agree', 'Agree'), ('disagree', 'Disagree')], max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('poll', 'user')  # Only one response per user per poll

class HealthEvent(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    place = models.CharField(max_length=100)
    panchayath = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class EventFeedback(models.Model):
    event = models.ForeignKey(HealthEvent, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    response = models.CharField(max_length=10, choices=[('like', 'Like'), ('dislike', 'Dislike')])

    class Meta:
        unique_together = ('event', 'user')


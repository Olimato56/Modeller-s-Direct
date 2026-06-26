from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_delete
from django.dispatch import receiver

class Tags(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    posttitle = models.TextField(blank=True, null=True, max_length=2000)
    slug = models.SlugField(unique=True)
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    posttype = models.CharField(max_length=1, choices=[('T', 'Text'), ('I', 'Image')], default='T')
    posttext = models.TextField(blank=True, null=True, max_length=5000)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tags, related_name='tagged', blank=True)

    def __str__(self):
        return self.posttitle

class PostImages(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='post_images/gallery/')   

class PostReplies(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='replies')
    reply = models.TextField(blank=True, null=True, max_length=5000)
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_replies', blank=True)



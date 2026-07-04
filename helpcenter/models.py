from django.db import models
from django.contrib.auth.models import User


class BeginnerTip(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='beginner_tips/gallery/', null=True, blank=True)

    def __str__(self):
        return self.title

class UserTipProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tip = models.ForeignKey(BeginnerTip, on_delete=models.CASCADE, related_name="completed_by")
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'tip') 

    def __str__(self):
        return f"{self.user.username} read {self.tip.title}"
    
class Tags(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class UserHelp(models.Model):
    helptitle = models.TextField(blank=True, null=True, max_length=2000)
    slug = models.SlugField(unique=True)
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    helptext = models.TextField(blank=True, null=True, max_length=5000)
    likes = models.ManyToManyField(User, related_name='liked_help', blank=True)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tags, related_name='taggedtips', blank=True)
    image = models.ImageField(upload_to='help_tips/gallery/', null=True, blank=True)

    def __str__(self):
        return self.helptitle
    
class HelpReplies(models.Model):
    userhelp = models.ForeignKey(UserHelp, on_delete=models.CASCADE, related_name='replies')
    reply = models.TextField(blank=True, null=True, max_length=5000)
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_helpreplies', blank=True)
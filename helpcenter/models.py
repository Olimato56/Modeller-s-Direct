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
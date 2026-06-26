from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=1000)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    objectID = models.PositiveIntegerField(null=True, blank=True)
    targetObject = GenericForeignKey('category', 'objectID')

    class Meta:
        ordering = ['-timestamp']



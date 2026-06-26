from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_delete
from django.dispatch import receiver
from google import genai
from django.db.models.signals import post_save
import os
from django.conf import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def current_year():
    return datetime.date.today().year

class Country(models.Model):
    name=models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class CarManufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='models')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
class BodyType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
class RoadRace(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Scale(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
class Detail(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class ModelKit(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, related_name='models')
    carmanufacturer = models.ForeignKey(CarManufacturer, on_delete=models.PROTECT, related_name='models', null=True)
    bodytype = models.ForeignKey(BodyType, on_delete=models.PROTECT, related_name='models', null=True)
    roadrace = models.ForeignKey(RoadRace, on_delete=models.PROTECT, related_name='models', null=True)
    detail = models.ForeignKey(Detail, on_delete=models.PROTECT, related_name='models', null=True)
    totalviews = models.PositiveIntegerField(default=0)
    yearoftool = models.PositiveIntegerField(default=2000, validators=[MinValueValidator(1900), MaxValueValidator(current_year())], blank=True)
    modelyear = models.PositiveIntegerField(default=2000, validators=[MinValueValidator(1900), MaxValueValidator(current_year())])
    scale = models.ForeignKey(Scale, on_delete=models.PROTECT, related_name='models', null=True)
    descriptionInput = models.TextField(blank=True, null=True) 
    descriptionReport = models.BooleanField(default=False)
    reportReason = models.TextField(blank=True, null=True)
    coverimage = models.ImageField(upload_to='model_images/cover', null=True, blank=True)
    status = models.CharField(max_length=1, choices=[('P', 'Pending'), ('A', 'Approved'), ('R', 'Rejected')], default='P')
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.manufacturer.name} {self.name}"
    
@receiver(post_save, sender=ModelKit)
def generateDescription(sender, instance, created, **kwargs):
    if created:
        prompt = f"Write 3 short, formal sentences about the detail, parts included and special features of the {instance.carmanufacturer}  { instance.name} by {instance.manufacturer}. Be formal and precise, you're writing a product description."

        try: 
            response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            ModelKit.objects.filter(pk=instance.pk).update(descriptionInput=response.text)
        except Exception as ex:
            print(f"Gemini error: {ex}")
        

@receiver(post_delete, sender=ModelKit)
def deleteCoverImage(sender, instance, **kwargs):
    if instance.coverimage:
        instance.coverimage.delete(save=False)

class TipIssue(models.Model):
    model_kit = models.ForeignKey(ModelKit, on_delete=models.CASCADE, related_name='tips')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_tips', blank=True)

class CompletedModel(models.Model):
    model_kit = models.ForeignKey(ModelKit, on_delete=models.CASCADE, related_name='builds')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    caption = models.TextField(blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='liked_builds', blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['model_kit', 'user'], name='unique_user_completed_model')
        ]

class BuildModels(models.Model):
    build = models.ForeignKey(CompletedModel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='model_images/gallery/')

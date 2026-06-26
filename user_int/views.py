from modeldatabase.models import ModelKit, TipIssue, CompletedModel
from forum.models import Post
from django.apps import apps
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.contrib import messages
from django.http import HttpResponse
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image, ImageOps
import sys, os
from notifications.models import notification


def home(request):
    all_models = ModelKit.objects.filter(status='A').order_by('-totalviews')
    models = all_models[:10]
    all_posts = Post.objects.order_by('-views')
    posts = all_posts[:10]

    return render(request, "home.html", {'models': models, 'posts': posts})

#handle text submission
def handle_text_submission(request, model_class, post_key='submit_tip', **kwargs):
    if post_key in request.POST:
        message = request.POST.get('message')
        if message:
            model_class.objects.create(
                **kwargs
            )
            return True
    return False

def like_item(request, objid, objectDb, type):
    if request.user.is_authenticated:
        object = get_object_or_404(objectDb, id=objid)
        if request.user in object.likes.all():
            object.likes.remove(request.user)
        else:
            object.likes.add(request.user)
            owner = getattr(object, 'poster', getattr(object, 'user', None))
            likesNotification(object, owner, type)
            
    return HttpResponse(str(object.likes.count()))

def likesNotification(item, creator, type):
    like_count = item.likes.count()
    if like_count == 10:
        notification.objects.create(recipient=creator, message=f"Your {type} got 10 likes!", targetObject = item)
    elif like_count == 50:
        notification.objects.create(recipient=creator, message=f'<i class="fa-regular fa-fire"></i> Your {type} got 50 likes!', targetObject = item)
    elif like_count == 100:
        notification.objects.create(recipient=creator, message=f'<i class="fa-solid fa-fire"></i> Your {type} got 100 likes!', targetObject = item)

def report(request, model, modelField, reason=None):
    if request.user.is_authenticated:
        currentValue = getattr(model, modelField, False)

        if not currentValue: 
            setattr(model, modelField, True)
            if reason:
                model.reportReason = reason
            model.save()

def compress_image(file):

    img = Image.open(file)
    img = ImageOps.exif_transpose(img)
    
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    max_size = (1200, 1200)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    output = BytesIO()
    img.save(output, format='JPEG', quality=60) 
    output.seek(0)
    
    base_name = os.path.splitext(file.name)[0] 

    true_file_size = output.getbuffer().nbytes

    compressed_file = InMemoryUploadedFile(
        output, 
        'ImageField', 
        f"{base_name}.jpg", 
        'image/jpeg', 
        true_file_size, 
        None
    )
    return compressed_file
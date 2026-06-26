from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import BeginnerTip, UserTipProgress
from django.http import HttpResponse

def helpcenter(request):
    
    context = {

    }

    return render(request, "helpcenter.html", context)



def beginnerhelp(request):
    all_beginner_tips = BeginnerTip.objects.all()
    completed_tip_ids = []
    
    if request.user.is_authenticated:
        completed_tip_ids = UserTipProgress.objects.filter(
            user=request.user, 
            completed=True
        ).values_list('tip_id', flat=True)

    context = {
        'all_beginner_tips': all_beginner_tips,
        'completed_tip_ids': completed_tip_ids
    }

    return render(request, "beginnerhelp.html", context)

def toggle_tip_completion(request, tip_id):
    if request.user.is_authenticated:
        progress = UserTipProgress.objects.filter(user=request.user, tip_id=tip_id)
        
        if progress.exists():
            progress.delete()
            return HttpResponse('<i class="fa-regular fa-circle"></i> Mark As Understood')
        else:
            UserTipProgress.objects.create(user=request.user, tip_id=tip_id, completed=True)
            return HttpResponse('<i class="fa-solid fa-check-circle"></i> Done!')
            

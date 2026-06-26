from django.shortcuts import render
from .models import notification
from django.contrib.auth.decorators import login_required

@login_required
def inbox(request):
    notifications = list(request.user.notifications.all().order_by('-timestamp'))
    request.user.notifications.filter(is_read=False).update(is_read=True)

    return render(request, 'inbox.html', {'notifications': notifications})

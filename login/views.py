from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django_otp.plugins.otp_email.models import EmailDevice
from django.contrib.auth.models import User

def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            request.session['pre_2fa_user_id'] = user.id
            return redirect('twofa')
        else:
            return render(request, "login.html", {"error": "Invalid Credentials"})
    return render(request, "login.html")



def twofa_verify(request):
    user_id = request.session.get('pre_2fa_user_id')

    if not user_id:
        return redirect('login')
    
    user = User.objects.get(id=user_id)
    device, created = EmailDevice.objects.get_or_create(user=user, name="default")

    if request.method == 'POST':
        token = request.POST.get("otp_token")

        if device.verify_token(token):
            login(request, user)
            del request.session['pre_2fa_user_id']
            return redirect('home')
        else:
            return render(request, "twofa.html", {"error": "Invalid or expired code"})
        
    if request.method == 'GET':
        device.generate_challenge()

    return render(request, "twofa.html", {'user': user})



def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = request.POST.get('email')
            user.save()
            return redirect('twofa')
        else: 
            return render(request, "register.html", {"errors": form.errors})
    else:
        form = UserCreationForm()

    return render(request, "register.html", {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')



from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name="login"),
    path('register/', views.register, name="register"),
    path('twofa/', views.twofa_verify, name="twofa"),
]
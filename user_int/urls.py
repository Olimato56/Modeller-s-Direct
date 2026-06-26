from django.urls import path
from . import views
from login import views as auth_views

urlpatterns = [
    path('', views.home, name="home"),
    path('logout/', auth_views.logout_view, name='logout')
]
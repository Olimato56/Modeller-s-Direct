from django.urls import path
from . import views
from login import views as auth_views

urlpatterns = [
    path('', views.helpcenter, name="helpcenter"),
    path('beginnerhelp/', views.beginnerhelp, name="beginnerhelp"),
    path('toggle-complete/<int:tip_id>/', views.toggle_tip_completion, name='toggle-complete-tip'),
]
from django.urls import path
from .views import userprofile

urlpatterns = [
    path('', userprofile, name="userprofile"),
]
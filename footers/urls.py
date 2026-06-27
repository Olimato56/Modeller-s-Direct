from django.urls import path
from .views import contact, TOS, privacypolicy

urlpatterns = [
    path('contact/', contact, name="contact"),
    path('TOS/', TOS, name="TOS"),
    path('privacypolicy/', privacypolicy, name="privacypolicy"),
]
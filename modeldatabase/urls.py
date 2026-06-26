from django.urls import path
from . import views
from user_int.views import like_item
from .models import TipIssue, CompletedModel

urlpatterns = [
    path('', views.databasehome, name="databasehome"),
    path('submitmodel/', views.submit_model, name="submitmodel"),
    path('tips/<int:objid>/like/', like_item, {'objectDb': TipIssue, 'type': 'tip'}, name='like-tip'),
    path('builds/<int:objid>/like/', like_item, {'objectDb': CompletedModel, 'type': 'finished build'}, name='like-build'),
    path('<slug:model_slug>/', views.car_template, name="car-template")
    
]
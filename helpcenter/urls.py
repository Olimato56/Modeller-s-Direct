from django.urls import path
from . import views
from login import views as auth_views
from user_int.views import like_item
from .models import UserHelp, HelpReplies


urlpatterns = [
    path('', views.helpcenter, name="helpcenter"),
    path('beginnerhelp/', views.beginnerhelp, name="beginnerhelp"),
    path('userhelp/', views.userhelp, name="userhelp"),
    path('toggle-complete/<int:tip_id>/', views.toggle_tip_completion, name='toggle-complete-tip'),
    path('post/<int:objid>/like/', like_item, {'objectDb': UserHelp, 'item_type': 'post'}, name='like_help'),
    path('reply/<int:objid>/like/', like_item, {'objectDb': HelpReplies, 'item_type': 'reply'}, name='like_reply'),
    path('submithelp/', views.submit_help, name="submithelp"),
    path('<slug:help_slug>/', views.userhelp_template, name="userhelp-template"),
]
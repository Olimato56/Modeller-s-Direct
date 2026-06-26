from django.urls import path
from .views import submit_post, post_template, forum
from user_int.views import like_item
from .models import Post, PostReplies

urlpatterns = [
    path('', forum, name="forum"),
    path('post/<int:objid>/like/', like_item, {'objectDb': Post, 'type': 'post'}, name='like_post'),
    path('reply/<int:objid>/like/', like_item, {'objectDb': PostReplies, 'type': 'reply'}, name='like_reply'),
    path('submitpost/', submit_post, name="submitpost"),
    path('<slug:post_slug>/', post_template, name="post-template"),
]
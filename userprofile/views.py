from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Sum
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from forum.models import Post, PostReplies
from modeldatabase.models import TipIssue, CompletedModel

@login_required
def userprofile(request):
    
    profile_user = request.user

    total_posts = Post.objects.filter(poster=profile_user).count()
    total_replies = PostReplies.objects.filter(poster=profile_user).count()
    total_tips  = TipIssue.objects.filter(user=profile_user).count()
    total_builds  = CompletedModel.objects.filter(user=profile_user).count()

    #calculate total likes recieved by the user
    post_likes_stats = Post.objects.filter(poster=profile_user).annotate(likes_count=Count('likes')).aggregate(total=Sum('likes_count'))
    post_likes = post_likes_stats['total'] or 0
    reply_likes_stats = PostReplies.objects.filter(poster=profile_user).annotate(likes_count=Count('likes')).aggregate(total=Sum('likes_count'))
    reply_likes = reply_likes_stats['total'] or 0
    tips_likes_stats = TipIssue.objects.filter(user=profile_user).annotate(likes_count=Count('likes')).aggregate(total=Sum('likes_count'))
    tips_likes = tips_likes_stats['total'] or 0
    build_likes_stats = CompletedModel.objects.filter(user=profile_user).annotate(likes_count=Count('likes')).aggregate(total=Sum('likes_count'))
    build_likes = build_likes_stats['total'] or 0

    total_likes = post_likes + reply_likes + tips_likes + build_likes

    user_posts = Post.objects.filter(poster=profile_user).order_by('-created_at')

    context = {
        'profile_user': profile_user, 
        'total_posts': total_posts,
        'total_replies': total_replies,
        'total_likes': total_likes,
        'total_tips': total_tips,
        'total_builds': total_builds,
        'user_posts': user_posts
    }

    return render(request, "userprofile.html", context)
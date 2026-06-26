from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, PostImages, PostReplies, Tags
from django.db.models import Q, Count
from user_int.views import like_item, handle_text_submission, report, compress_image
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .submitpost import PostSubmission
from django.utils.text import slugify
from notifications.models import notification



def forum(request):
    limit = int(request.GET.get('limit', 10))
    query = request.GET.get('q', '')
    sort_option = request.GET.get('sort', 'default')

    all_posts = Post.objects.all()

    all_tags = Tags.objects.all()

    selected_tags = request.GET.getlist('tags')

    if selected_tags:
        matching_post_ids = Post.objects.filter(tags__id__in=selected_tags).values_list('id', flat=True)
        all_posts = all_posts.filter(id__in=matching_post_ids)

    #handle searching
    if query:
        search_terms = query.split()
        for term in search_terms:
            all_posts = all_posts.filter(
                Q(posttitle__icontains = term) |
                Q(posttext__icontains = term)
            ).distinct()

    #handle sorting
    if sort_option == 'views':
        all_posts = all_posts.annotate(like_count=Count('likes', distinct=True)).order_by('-views', '-like_count', 'posttitle')
    elif sort_option == 'viewslow':
        all_posts = all_posts.annotate(like_count=Count('likes', distinct=True)).order_by('views', '-like_count', 'posttitle')
    elif sort_option == 'likes':
        all_posts = all_posts.annotate(like_count=Count('likes', distinct=True)).order_by('-like_count', '-views')
    elif sort_option == 'oldest':
        all_posts = all_posts.order_by('created_at', '-views')
    elif sort_option == 'newest':
        all_posts = all_posts.order_by('-created_at', '-views')
    elif sort_option == 'replies':
        all_posts = all_posts.annotate(reply_count=Count('replies', distinct=True)).order_by('-reply_count', '-views')
    else:
        all_posts = all_posts.annotate(like_count=Count('likes', distinct=True)).order_by('-views', '-like_count', 'posttitle')

    all_posts = all_posts.distinct()

    params = request.GET.copy()
    if 'limit' in params:
        del params['limit']
    url_params = params.urlencode()

    total_count = all_posts.count()
    posts = all_posts[:limit]
    next_limit = limit + 10

    liked_posts = []
    if request.user.is_authenticated:
        liked_posts = request.user.liked_posts.values_list('id', flat=True)


    context = {
        'posts': posts, 
        'url_params': url_params,
        'next_limit': next_limit,
        'current_limit': limit,
        'total_count': total_count,
        'query': query,
        'sort': sort_option,
        'liked_posts': liked_posts, 
        'all_tags': all_tags, 
        'selected_tags': selected_tags
    }

    return render(request, "forum.html", context)

def post_template(request, post_slug):
    post = get_object_or_404(Post, slug=post_slug)
    session_key = f'viewed_post_{post.posttitle}'

    if not request.session.get(session_key, False):
        post.views += 1
        post.save(update_fields=['views'])
        request.session[session_key] = True

    if request.method == 'POST' and request.user.is_authenticated:
        if 'submit_reply' in request.POST:
            message = request.POST.get('message')
            if message:
                if handle_text_submission(request, PostReplies, 'submit_reply', post=post, reply=message, poster=request.user):
                    replyNotification(post, request.user)
                    return redirect('post-template', post_slug=post_slug)

    is_liked = False
    if request.user.is_authenticated:
        is_liked = post.likes.filter(id=request.user.id).exists()

    replies = PostReplies.objects.filter(post=post).order_by('-created_at')
    liked_replies = replies.filter(likes=request.user).values_list('id', flat=True) if request.user.is_authenticated else []

    return render(request, "post-template.html", {'post': post, 'is_liked': is_liked, 'replies': replies, 'liked_replies': liked_replies})

@login_required
def submit_post(request):
    if request.method == "POST":
        form = PostSubmission(request.POST, request.FILES)
        if form.is_valid():
            uploaded_images = request.FILES.getlist('images_field')

            if len(uploaded_images) > 5:
                form.add_error(None, "You can only upload a maximum of 5 images.")
                return render(request, 'submit_post.html', {'form': form})
            
            post = form.save(commit=False)

            post.poster = request.user
            post.slug = slugify(post.posttitle)

            post.save()

            selected_tag_ids = request.POST.getlist('tags')
            clean_tag_ids = [tag_id for tag_id in selected_tag_ids if tag_id.isdigit()]
            post.tags.set(clean_tag_ids)

            if uploaded_images:
                for image_file in uploaded_images:
                    try:
                        compressed_file = compress_image(image_file)
                        PostImages.objects.create(post=post, image=compressed_file)
                    except Exception:
                        pass

            return redirect('/forum')
    else:
        form = PostSubmission()

    all_tags = Tags.objects.all()

    return render(request, 'submit_post.html', {'form': form, 'tagged': all_tags})

def replyNotification(post, replier):
    truncated_text = post.posttext[:50] + "..." if len(post.posttitle) > 50 else post.posttitle
    notification.objects.create(recipient=post.poster, message=f"{replier} replied to your post, '{truncated_text}'", targetObject = post)

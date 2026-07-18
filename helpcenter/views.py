from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import BeginnerTip, UserTipProgress, UserHelp, Tags, HelpReplies
from django.http import HttpResponse
from user_int.views import like_item, handle_text_submission, report, compress_image
from django.db.models import Q, Count
from notifications.models import notification
from .submittip import TipSubmission
from django.utils.text import slugify



def helpcenter(request):
    
    context = {

    }

    return render(request, "helpcenter.html", context)



def beginnerhelp(request):
    all_beginner_tips = BeginnerTip.objects.all()
    completed_tip_ids = []
    
    if request.user.is_authenticated:
        completed_tip_ids = UserTipProgress.objects.filter(
            user=request.user, 
            completed=True
        ).values_list('tip_id', flat=True)

    context = {
        'all_beginner_tips': all_beginner_tips,
        'completed_tip_ids': completed_tip_ids
    }

    return render(request, "beginnerhelp.html", context)

def toggle_tip_completion(request, tip_id):
    if request.user.is_authenticated:
        progress = UserTipProgress.objects.filter(user=request.user, tip_id=tip_id)
        
        if progress.exists():
            progress.delete()
            return HttpResponse('<i class="fa-regular fa-circle"></i> Mark As Understood')
        else:
            UserTipProgress.objects.create(user=request.user, tip_id=tip_id, completed=True)
            return HttpResponse('<i class="fa-solid fa-check-circle"></i> Done!')
        
def userhelp(request):
    limit = int(request.GET.get('limit', 10))
    query = request.GET.get('q', '')
    sort_option = request.GET.get('sort', 'default')

    all_help = UserHelp.objects.all()

    all_tags = Tags.objects.all()

    selected_tags = request.GET.getlist('tags')

    if selected_tags:
        matching_help_ids = UserHelp.objects.filter(tags__id__in=selected_tags).values_list('id', flat=True)
        all_help = all_help.filter(id__in=matching_help_ids)

    #handle searching
    if query:
        search_terms = query.split()
        for term in search_terms:
            all_help = all_help.filter(
                Q(helptitle__icontains = term) |
                Q(helptext__icontains = term)
            ).distinct()

    #handle sorting
    if sort_option == 'views':
        all_help = all_help.annotate(like_count=Count('likes', distinct=True)).order_by('-views', '-like_count', 'helptitle')
    elif sort_option == 'viewslow':
        all_help = all_help.annotate(like_count=Count('likes', distinct=True)).order_by('views', '-like_count', 'helptitle')
    elif sort_option == 'likes':
        all_help = all_help.annotate(like_count=Count('likes', distinct=True)).order_by('-like_count', '-views')
    elif sort_option == 'oldest':
        all_help = all_help.order_by('created_at', '-views')
    elif sort_option == 'newest':
        all_help = all_help.order_by('-created_at', '-views')
    elif sort_option == 'replies':
        all_help = all_help.annotate(reply_count=Count('replies', distinct=True)).order_by('-reply_count', '-views')
    else:
        all_help = all_help.annotate(like_count=Count('likes', distinct=True)).order_by('-views', '-like_count', 'helptitle')

    all_help = all_help.distinct()

    params = request.GET.copy()
    if 'limit' in params:
        del params['limit']
    url_params = params.urlencode()

    total_count = all_help.count()
    helps = all_help[:limit]
    next_limit = limit + 10

    liked_help = []
    if request.user.is_authenticated:
        liked_help = request.user.liked_help.values_list('id', flat=True)


    context = {
        'helps': helps, 
        'url_params': url_params,
        'next_limit': next_limit,
        'current_limit': limit,
        'total_count': total_count,
        'query': query,
        'sort': sort_option,
        'liked_help': liked_help, 
        'all_tags': all_tags, 
        'selected_tags': selected_tags
    }

    return render(request, "userhelp.html", context)

def userhelp_template(request, help_slug):
    help = get_object_or_404(UserHelp, slug=help_slug)
    session_key = f'viewed_help_{help.helptitle}'

    if not request.session.get(session_key, False):
        help.views += 1
        help.save(update_fields=['views'])
        request.session[session_key] = True

    if request.method == 'POST' and request.user.is_authenticated:
        if 'submit_reply' in request.POST:
            message = request.POST.get('message')
            if message:
                if handle_text_submission(request, HelpReplies, 'submit_reply', userhelp=help, reply=message, poster=request.user):
                    replyNotification(help, request.user)
                    return redirect('userhelp-template', help_slug=help_slug)

    is_liked = False
    if request.user.is_authenticated:
        is_liked = help.likes.filter(id=request.user.id).exists()

    replies = HelpReplies.objects.filter(userhelp=help).order_by('-created_at')
    liked_helpreplies = replies.filter(likes=request.user).values_list('id', flat=True) if request.user.is_authenticated else []

    return render(request, "userhelp-template.html", {'help': help, 'is_liked': is_liked, 'replies': replies, 'liked_helpreplies': liked_helpreplies})

def replyNotification(help, replier):
    truncated_text = help.helptext[:50] + "..." if len(help.helptitle) > 50 else help.helptitle
    notification.objects.create(recipient=help.poster, message=f"{replier} replied to your tip, '{truncated_text}'", targetObject = help)

@login_required
def submit_help(request):
    if request.method == "POST":
        form = TipSubmission(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = request.FILES.get('image_field')
            
            help = form.save(commit=False)

            help.poster = request.user
            help.slug = slugify(help.helptitle)

            help.save()

            selected_tag_ids = request.POST.getlist('tags')
            clean_tag_ids = [tag_id for tag_id in selected_tag_ids if tag_id.isdigit()]
            help.tags.set(clean_tag_ids)

            if uploaded_image:
                try:
                    compressed_file = compress_image(uploaded_image)
                    help.image = compressed_file
                except Exception:
                    return 'error'
                
            help.save()

            return redirect('/helpcenter/userhelp')
    else:
        form = TipSubmission()

    all_tags = Tags.objects.all()

    return render(request, 'submit_help.html', {'form': form, 'tagged': all_tags})     

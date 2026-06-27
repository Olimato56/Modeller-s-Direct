from django.shortcuts import render, get_object_or_404, redirect
from .models import ModelKit, Manufacturer, CarManufacturer, Country, BodyType, RoadRace, Detail, TipIssue, BuildModels, CompletedModel
from django.db.models import Q
from .submitmodel import ModelKitSubmission
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.text import slugify
from notifications.models import notification
from django.contrib import messages
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from user_int.views import handle_text_submission, report, compress_image


def databasehome(request):
    #initial parameters
    limit = int(request.GET.get('limit', 10))
    query = request.GET.get('q', '')
    sort_option = request.GET.get('sort', 'default')

    #find all selected filters
    selected_kit_manus = request.GET.getlist('kit_manu')
    selected_car_manus = request.GET.getlist('car_manu')
    selected_countries = request.GET.getlist('country')
    selected_bodytype = request.GET.getlist('bodytype')
    selected_roadrace = request.GET.getlist('roadrace')
    selected_detail = request.GET.getlist('detail')

    #finding all models
    all_models = ModelKit.objects.filter(status='A').order_by('carmanufacturer__name', 'name')

    #apply filters
    if selected_kit_manus:
        all_models = all_models.filter(manufacturer__name__in=selected_kit_manus)
    
    if selected_car_manus:
        all_models = all_models.filter(carmanufacturer__name__in=selected_car_manus)

    if selected_countries:
        all_models = all_models.filter(carmanufacturer__country__name__in=selected_countries)

    if selected_bodytype:
        all_models = all_models.filter(bodytype__name__in=selected_bodytype)

    if selected_roadrace:
        all_models = all_models.filter(roadrace__name__in=selected_roadrace)

    if selected_detail:
        all_models = all_models.filter(detail__name__in=selected_detail)

    #search query
    if query:
        search_terms = query.split()
        for term in search_terms: 
            all_models = all_models.filter(
                Q(name__icontains=term) |
                Q(description__icontains=term) |
                Q(manufacturer__name__icontains=term) |
                Q(carmanufacturer__name__icontains=term) |
                Q(bodytype__name__icontains=term)
            ).distinct()

    #sorting
    if sort_option == 'manufacturer':
        all_models = all_models.order_by('manufacturer__name', 'name')
    elif sort_option == 'automanu':
        all_models = all_models.order_by('carmanufacturer__name', 'name')
    elif sort_option == 'age':
        all_models = all_models.order_by('-yearoftool')
    elif sort_option == 'modelyearnew':
        all_models = all_models.order_by('-modelyear')
    elif sort_option == 'modelyearold':
        all_models = all_models.order_by('modelyear')
    elif sort_option == 'views':
        all_models = all_models.order_by('-views')
    else:
        all_models = all_models.order_by('carmanufacturer__name')

    #copy the filters/sort/search in the url and then remove the current limit, then increment the limit and paste the old url back in
    params = request.GET.copy()
    if 'limit' in params:
        del params['limit']
    url_params = params.urlencode()

    total_count = all_models.count()
    models = all_models[:limit]
    next_limit = limit + 10

    manufacturers = Manufacturer.objects.all().order_by('name')
    carmanufacturers = CarManufacturer.objects.all().order_by('name')
    bodytypes = BodyType.objects.all().order_by('name')
    roadrace = RoadRace.objects.all().order_by('name')
    country = Country.objects.all()
    detail = Detail.objects.all()

    context = {
        'models': models, 
        'selected_kit_manus': selected_kit_manus,
        'selected_car_manus': selected_car_manus,
        'selected_countries': selected_countries,
        'selected_bodytype': selected_bodytype,
        'selected_roadrace': selected_roadrace,
        'selected_detail': selected_detail,
        'manufacturers': manufacturers, 
        'carmanufacturers': carmanufacturers, 
        'countries': country, 
        'bodytypes': bodytypes, 
        'roadrace':roadrace,
        'details': detail,
        'url_params': url_params,
        'next_limit': next_limit,
        'current_limit': limit,
        'total_count': total_count,
        'query': query,
        'sort': sort_option
    }
    
    return render(request, "databasehome.html", context)


def car_template(request, model_slug):
    model = get_object_or_404(ModelKit, slug=model_slug)

    session_key = f'viewed_kit_{model.name}'
    if not request.session.get(session_key, False):
        model.totalviews += 1
        model.save(update_fields=['totalviews'])
        request.session[session_key] = True

    if request.method == 'POST' and request.user.is_authenticated:
        #code to process user's submitted tip and load them all
        if 'submit_tip' in request.POST:
            message = request.POST.get('message')
            if message:
                if handle_text_submission(request, TipIssue, 'submit_tip', model_kit=model, user=request.user, message=message): #note this is the default case for the key
                    return redirect('car-template', model_slug=model_slug)
            
        #process submission of build images
        elif 'upload_build' in request.POST:
            files = request.FILES.getlist('images_field')
            caption = request.POST.get('caption')
            if files:
                build, created = CompletedModel.objects.get_or_create(model_kit=model, user=request.user)
                existing_count = build.images.count()
                slots_left = 6 - existing_count

                if len(files) > slots_left:                    
                    messages.error(request, "Too Many Images Uploaded: You have reached the limit of 6 photos.")
                    return redirect('car-template', model_slug=model_slug)
                
                files_to_upload = files[:slots_left]

                for file in files_to_upload:
                    try:
                        compressed_file = compress_image(file)
                        BuildModels.objects.create(build=build, image=compressed_file)
                    except Exception:
                        pass
                    
                build.caption = caption
                build.save()
            return redirect('car-template', model_slug=model_slug)
        
        elif 'report' in request.POST:
            reason = request.POST.get('reason', '')
            report(request, model, 'descriptionReport', reason)
            return redirect('car-template', model_slug=model_slug)

    tips = TipIssue.objects.filter(model_kit=model).order_by('-likes')
    liked_tips = tips.filter(likes=request.user).values_list('id', flat=True) if request.user.is_authenticated else []
    builds = model.builds.all().prefetch_related('images').order_by('-likes')
    liked_builds = builds.filter(likes=request.user).values_list('id', flat=True) if request.user.is_authenticated else []
    return render(request, 'car-template.html', {'model': model, 'tips': tips, 'liked_tips': liked_tips, 'builds': builds, 'liked_builds': liked_builds})


@login_required
def submit_model(request):
    if request.method == "POST":
        form = ModelKitSubmission(request.POST, request.FILES)
        if form.is_valid():
            kit = form.save(commit=False)
            kit.submitted_by = request.user
            kit.status = 'P'
            kit.slug = slugify(kit.name)
            kit.save()
            return redirect('/database')
    else:
        form = ModelKitSubmission()

    return render(request, 'submit_model.html', {'form': form})


def approveModel(kit):
    #creates the notification. is reusable
    notification.objects.create(recipient=kit.submitted_by, message=f"Your model {kit.carmanufacturer} { kit.name} was approved.", targetObject = kit)

def rejectModel(kit):
    notification.objects.create(recipient=kit.submitted_by, message=f"Your model {kit.carmanufacturer} { kit.name} was rejected due to: {kit.rejection_reason}")


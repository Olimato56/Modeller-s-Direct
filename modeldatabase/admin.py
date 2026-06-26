from django.contrib import admin
from .models import ModelKit, Country, CarManufacturer, Manufacturer, BodyType, RoadRace, Detail, Scale, TipIssue, BuildModels, CompletedModel
from notifications.models import notification
from .views import approveModel, rejectModel
from google import genai
from django.contrib import messages
from django.conf import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

class BuildModels(admin.TabularInline):
    model = BuildModels
    extra = 5  # Gives 5 empty slots for uploads

@admin.register(CompletedModel)
class CompletedModelAdmin(admin.ModelAdmin):
    list_display = ('model_kit', 'user', 'created_at')
    inlines = [BuildModels]

@admin.action(description="Regenerate Description")
def regenerateDescription(ModelAdmin, request, queryset): # Renamed 'models' to 'queryset' to avoid confusion with the AI
    success_count = 0

    for obj in queryset:
        prompt = f"Write 3 to 5 sentences about the detail, parts included and special features of the {obj.carmanufacturer} {obj.name} by {obj.manufacturer}. Focus heavily on any additional parts, whether the kit is kerbside or fully detailed, and include everything that soands out about the kit (example: a kit might feature rally lights or wider fenders). You don't need to sell the kit and don't use too many adjectives. Ensure everything you are saying is purely fact. Do not guess. This kit is {obj.detail}, make sure your answer aligns with this. For anything that is optional, make sure to mention that it is optional. Do not make something a necessecity if it isn't. Offer as much detailas possible without too many adjectives. Assume the user is knowldgable on model kits and it's jargon. This is a great example, try to follow this sort of format: The Hasegawa Lancia Stratos Custom is a 1/24 scale kerbside model, emphasizing external modifications and cockpit detail without an engine bay. It features wider, integrated front and rear fender flares and a prominent rear wing, molding a distinct wide-body appearance. The kit provides clear parts for the main lighting units, and an optional front bumper-mounted rally light pod with clear lenses is included. Builders can choose from multiple sets of wheels and corresponding wider tires to complete the stance. Inside, a detailed cockpit tub with separate bucket seats, a dashboard, and a roll cage is supplied, while the chassis underside features molded suspension and exhaust system details."
        
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            obj.descriptionInput = response.text 
            obj.save()
            success_count += 1
            
        except Exception as e: # Fixed 'ex' vs 'e' typo
            ModelAdmin.message_user(request, f"Error: {e} for model {obj.name}", messages.ERROR)

    if success_count > 0:
        ModelAdmin.message_user(request, f"Successfully generated {success_count} descriptions", messages.SUCCESS)

@admin.register(ModelKit)
class modelAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer', 'totalviews', 'status', 'descriptionReport')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'manufacturer', 'status')

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = self.model.objects.get(pk=obj.pk)
            if obj.status == 'A' and old_obj.status != 'A': 
                approveModel(obj)
            if obj.status == 'R' and old_obj.status != 'R': 
                rejectModel(obj)
        super().save_model(request, obj, form, change)

    actions = [regenerateDescription]

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(CarManufacturer)
class CarManufacturerAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(BodyType)
class BodyTypeAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(RoadRace)
class RoadRaceAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Detail)
class DetailAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Scale)
class ScaleAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(TipIssue)
class TipAdmin(admin.ModelAdmin):
    search_fields = ('created_at', )
    list_display = ('model_kit', 'user', 'message', )




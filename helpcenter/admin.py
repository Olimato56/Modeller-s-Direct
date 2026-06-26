from django.contrib import admin
from .models import BeginnerTip, UserTipProgress

@admin.register(BeginnerTip)
class modelAdmin(admin.ModelAdmin):
    list_display = ('title', )
    search_fields = ('title', )

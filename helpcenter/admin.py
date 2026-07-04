from django.contrib import admin
from .models import BeginnerTip, UserTipProgress, UserHelp, HelpReplies, Tags

@admin.register(BeginnerTip)
class modelAdmin(admin.ModelAdmin):
    list_display = ('title', )
    search_fields = ('title', )

@admin.register(UserHelp)
class tipAdmin(admin.ModelAdmin):
    list_display = ('helptitle', 'poster', 'views', 'created_at')
    prepopulated_fields = {'slug': ('helptitle',)}
    search_fields = ('helptitle', 'poster', 'helptext')

@admin.register(HelpReplies)
class ReplyAdmin(admin.ModelAdmin):
    search_fields = ('created_at', 'reply',)
    list_display = ('userhelp', 'poster', 'reply', )


@admin.register(Tags)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name',)
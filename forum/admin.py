from django.contrib import admin
from .models import Post, PostImages, PostReplies, Tags

class PostImagesInline(admin.TabularInline):
    model = PostImages
    extra = 5  # Gives 5 empty slots for uploads
    max_num = 5

@admin.register(Post)
class postAdmin(admin.ModelAdmin):
    list_display = ('posttitle', 'poster', 'posttype', 'views', 'created_at')
    prepopulated_fields = {'slug': ('posttitle',)}
    search_fields = ('posttitle', 'poster', 'posttext')

    inlines = [PostImagesInline]

@admin.register(PostReplies)
class ReplyAdmin(admin.ModelAdmin):
    search_fields = ('created_at', 'reply',)
    list_display = ('post', 'poster', 'reply', )


@admin.register(Tags)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name',)
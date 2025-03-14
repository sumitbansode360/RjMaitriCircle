from django.contrib import admin
from .models import Tag, Post, Follow, Stream, Like

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)  # Add search_fields here for autocomplete

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('caption', 'user', 'posted', 'likes')
    list_filter = ('posted', 'user')
    search_fields = ('caption',)
    autocomplete_fields = ('tag',)  # This requires TagAdmin to have search_fields

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following')

@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ('user', 'following', 'post', 'date')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post')



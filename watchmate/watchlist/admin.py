from django.contrib import admin
from .models import StreamPlatform, WatchList, Review
# Register your models here.

@admin.register(StreamPlatform)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'about', 'website']
    ordering = ['id']
    
@admin.register(WatchList)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'storyline', 'active', 'created']
    ordering = ['id']
    
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'review_user', 'rating', 'description', 'active', 'created', 'update']
    ordering = ['id']
    
    
    

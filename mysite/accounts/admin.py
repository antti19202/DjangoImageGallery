from django.contrib import admin
from .models import *
# Register your models here.

class PostAlbum(admin.ModelAdmin):
    list_display = ('user', 'title', 'description')
    search_fields = ['user']
    list_filter = ['user']

class PostPhoto(admin.ModelAdmin):
    list_display = ('user', 'album', 'image', 'title', 'description')
    search_fields = ['user']
    list_filter = ['date_created', 'user']


admin.site.register(Customer)
admin.site.register(Album, PostAlbum)
admin.site.register(Photo, PostPhoto)
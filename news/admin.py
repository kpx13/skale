# -*- coding: utf-8 -*-
from django.contrib import admin
from models import NewsItem
    
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'text')
    

admin.site.register(NewsItem, ItemAdmin)
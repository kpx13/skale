# -*- coding: utf-8 -*-
from django.contrib import admin
from models import Category, Item, LoadFromFile
"""
class ImageInline(admin.StackedInline): 
    model = Image
    extra = 3
"""
 
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'parent', 'order')
    
class ItemAdmin(admin.ModelAdmin):
    #inlines = [ ImageInline, ]
    list_display = ('name', 'art', 'category', 'price', 'price_old',)
    search_fields = ['art', 'name', 'id_1c']
    list_filter = ('category', )

class LoadAdmin(admin.ModelAdmin):
    list_display = ('date', 'to_update')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(LoadFromFile, LoadAdmin)

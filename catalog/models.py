# -*- coding: utf-8 -*-

from mptt.models import MPTTModel, TreeForeignKey
from django.db import models
from ckeditor.fields import RichTextField
import pytils
import datetime
from dashboard import string_with_title

class Category(MPTTModel):
    name = models.CharField(max_length=50, unique=True, verbose_name=u'название')
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', verbose_name=u'родительская категория')
    order = models.IntegerField(null=True, blank=True, default=0, verbose_name=u'порядок сортировки')
    slug = models.SlugField(max_length=128, verbose_name=u'слаг', unique=True, blank=True, help_text=u'заполнять не нужно')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug=pytils.translit.slugify(self.name)
        super(Category, self).save(*args, **kwargs)
        if self.order == 0:
            self.order = self.id
            self.save()
    
    @staticmethod
    def get_by_slug(page_name):
        try:
            return Category.objects.get(slug=page_name)
        except:
            return None
        
    def breadcrumb(self):
        page = self
        breadcrumbs = []
        while page:
            breadcrumbs.append(page)
            page = page.parent
        breadcrumbs.reverse()
        return breadcrumbs[:-1]
        
    class Meta:
        verbose_name = u'категория'
        verbose_name_plural = u'категории'
        ordering=['order']
        app_label = string_with_title("catalog", u"Каталог")

    
    class MPTTMeta:
        order_insertion_by = ['name']
        
    def __unicode__(self):
        return '%s%s' % (' -- ' * self.level, self.name)
    
    @staticmethod
    def get(id_):
        try:
            return Category.objects.get(id=id_)
        except:
            return None

class Item(models.Model):
    category = models.ForeignKey(Category, verbose_name=u'категория', related_name='items')
    name = models.CharField(max_length=512, verbose_name=u'название')
    art = models.CharField(max_length=50, verbose_name=u'артикул')
    price = models.FloatField(verbose_name=u'цена')
    price_old = models.FloatField(blank=True, null=True, verbose_name=u'старая цена (для акций)')
    description = RichTextField(default=u'', verbose_name=u'описание')
    image = models.ImageField(upload_to='uploads/items', max_length=256, blank=True, verbose_name=u'изображение')
    order = models.IntegerField(null=True, blank=True, verbose_name=u'порядок сортировки')
    novelty_home = models.BooleanField(blank=True, default=False, verbose_name=u'показывать на главной как новинку')
    recommend_home = models.BooleanField(blank=True, default=False, verbose_name=u'показывать на главной как рекомендуем')
    slug = models.SlugField(max_length=128, verbose_name=u'слаг', unique=True, blank=True, help_text=u'заполнять не нужно')
    date = models.DateTimeField(default=datetime.datetime.now, verbose_name=u'дата добавления')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug=pytils.translit.slugify(self.art)
        if self.order == 0:
            self.order = self.id
            self.save()
        super(Item, self).save(*args, **kwargs)
    
    @staticmethod
    def get_by_slug(page_name):
        try:
            return Item.objects.get(slug=page_name)
        except:
            return None

    @staticmethod
    def get(id_):
        try:
            return Item.objects.get(id=id_)
        except:
            return None
    
    @staticmethod
    def get_home():
        return Item.objects.filter(at_home=True, in_archive=False)
    
    def same_category(self):
        return Item.objects.filter(category=self.category, in_archive=False).exclude(id = self.id)
    
    def get_path(self):
        path = [self.category]
        while path[0].parent:
            path.insert(0, path[0].parent)
        return path
    
    class Meta:
        verbose_name = u'товар'
        verbose_name_plural = u'товары'
        ordering=['order']
        app_label = string_with_title("catalog", u"Каталог")
        
    def __unicode__(self):
        return self.name

"""
class Image(models.Model):
    item = models.ForeignKey(Item, verbose_name=u'товар', related_name='image')
    image = models.ImageField(upload_to='uploads/items', max_length=256, blank=True, verbose_name=u'изображение')
    order = models.IntegerField(null=True, blank=True, default=100, verbose_name=u'порядок сортировки')

    @staticmethod
    def get(id_):
        try:
            return Item.objects.get(id=id_)
        except:
            return None
    
    class Meta:
        verbose_name = u'изображение'
        verbose_name_plural = u'изображения'
        ordering=['order']
        app_label = string_with_title("catalog", u"Каталог")
        
    def __unicode__(self):
        return str(self.id) 
    
"""

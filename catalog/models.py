# -*- coding: utf-8 -*-

from mptt.models import MPTTModel, TreeForeignKey
from django.db import models
from ckeditor.fields import RichTextField
import pytils
import datetime
from dashboard import string_with_title
from django.db.models import Q


class Category(MPTTModel):
    name = models.CharField(max_length=127, verbose_name=u'название')
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', verbose_name=u'родительская категория')
    order = models.IntegerField(null=True, blank=True, default=0, verbose_name=u'порядок сортировки')
    slug = models.SlugField(max_length=127, verbose_name=u'слаг', unique=True, blank=True, help_text=u'заполнять не нужно')
    id_1c = models.CharField(max_length=50, unique=True, verbose_name=u'Идентификатор в 1C')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug=pytils.translit.slugify(self.name)[:100] + "-" + self.id_1c
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
    
    @staticmethod
    def has_id_1c(id_1c):
        return Category.objects.filter(id_1c=id_1c).count() > 0
    
    @staticmethod
    def get_by_id_1c(id_1c):
        if id_1c:
            return Category.objects.filter(id_1c=id_1c)[0]
        else:
            return None
        
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
        
    @staticmethod
    def search(query):
        return Category.objects.filter(Q(name__icontains=query))
    

class Item(models.Model):
    category = models.ForeignKey(Category, verbose_name=u'категория', related_name='items')
    name = models.CharField(max_length=512, verbose_name=u'название')
    art = models.CharField(max_length=50, verbose_name=u'артикул')
    price = models.FloatField(verbose_name=u'цена')
    price_old = models.FloatField(blank=True, null=True, verbose_name=u'старая цена (для акций)')
    description = RichTextField(default=u'', blank=True, verbose_name=u'описание вверху')
    description_bottom = RichTextField(default=u'', blank=True, verbose_name=u'описание внизу')
    image = models.ImageField(upload_to='uploads/items', max_length=256, blank=True, verbose_name=u'изображение')
    order = models.IntegerField(null=True, blank=True, verbose_name=u'порядок сортировки')
    novelty_home = models.BooleanField(blank=True, default=False, verbose_name=u'показывать на главной как новинку')
    recommend_home = models.BooleanField(blank=True, default=False, verbose_name=u'показывать на главной как рекомендуем')
    slug = models.SlugField(max_length=128, verbose_name=u'слаг', unique=True, blank=True, help_text=u'заполнять не нужно')
    date = models.DateTimeField(default=datetime.datetime.now, verbose_name=u'дата добавления')
    id_1c = models.CharField(max_length=50, unique=True, verbose_name=u'Идентификатор в 1C')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug=pytils.translit.slugify(self.name)[:100] + "-" + self.art
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
    def has_id_1c(id_1c):
        return Item.objects.filter(id_1c=id_1c).count() > 0
    
    @staticmethod
    def get_by_id_1c(id_1c):
        if id_1c:
            return Item.objects.filter(id_1c=id_1c)[0]
        else:
            return None
        
    @staticmethod
    def search(query):
        return Item.objects.filter(Q(name__icontains=query) |
                                   Q(art__icontains=query) |
                                   Q(description__icontains=query) |
                                   Q(description_bottom__icontains=query))
    
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


class LoadFromFile(models.Model):
    file = models.FileField(upload_to='uploads/data', max_length=256, verbose_name=u'файл')
    date = models.DateTimeField(default=datetime.datetime.now, verbose_name=u'дата загрузки')
    to_update = models.BooleanField(default=True, blank=True, verbose_name=u'нужно только обновление?', 
                                    help_text=u'Если галочка стоит, то будет только обновляться цена, если не стоит, то каталог обновится полностью (!!!)')
    log = models.TextField(blank=True, help_text=u'По завершению загрузки здесь появится лог.', verbose_name=u'лог загрузки')

    
    class Meta:
        verbose_name = u'загрузка'
        verbose_name_plural = u'загрузки'
        ordering=['-date']
        app_label = string_with_title("catalog", u"Каталог")
        
    def __unicode__(self):
        return str(self.date) 
    
    def save(self, *args, **kwargs):
        super(LoadFromFile, self).save(*args, **kwargs)
        if not self.log:
            from catalog.parse import go
            self.log = go(self.file, self.to_update)
            self.save()

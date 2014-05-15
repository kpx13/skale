 # -*- coding: utf-8 -*-

import sys
import re
from django.conf import settings
from catalog.models import Category, Item
from xml.dom import minidom

def go_categories(xmldoc, log):
    categorieslist = xmldoc.getElementsByTagName(u'Группа')
    Category.objects.all().delete()
    cicle = True
    while cicle:
        count_a = Category.objects.all().count()
        for s in categorieslist:
            id = s.attributes[u'Идентификатор'].value
            name = s.attributes[u'Наименование'].value
            try:
                parent_id = s.attributes[u'Родитель'].value
            except:
                parent_id = None
            if (parent_id is None) or Category.has_id_1c(parent_id):
                if not Category.has_id_1c(id):
                    Category(name=name,
                         parent=Category.get_by_id_1c(parent_id),
                         id_1c=id).save()
            else:
                pass
                #print 'NOTSAVED: %s - %s - %s' % (id, name, parent_id)
        cicle = Category.objects.all().count() > count_a
    log.append(u'Категории загружены успешно.')
        
def go_items(xmldoc, log):
    itemslist = xmldoc.getElementsByTagName(u'Товар')
    Item.objects.all().delete()
    
    for i in itemslist:
        id = i.attributes[u'Идентификатор'].value
        name = i.attributes[u'Наименование'].value
        parent_id = i.attributes[u'Родитель'].value # категория
        desc_list = xmldoc.getElementsByTagName(u'ЗначениеСвойства')
        description = ''
        description_bottom = ''
        for d in desc_list:
            if d.attributes[u'ИдентификаторСвойства'].value == u'ПолноеНаименование':
                description = d.attributes[u'Значение'].value
            elif d.attributes[u'ИдентификаторСвойства'].value == u'Комментарий':
                description_bottom = d.attributes[u'Значение'].value 

        if Category.has_id_1c(parent_id):
            Item(name=name,
                 category=Category.get_by_id_1c(parent_id),
                 id_1c=id,
                 art=id,
                 price=0,
                 description=description,
                 description_bottom=description_bottom).save()
        else:
            log.append(u'Не загружен товар с идентификатором %s. Нет родительской категории %s.'% (id, parent_id))
    log.append(u'Товары загружены успешно.')
            
def go_prices(xmldoc, log):
    itemslist = xmldoc.getElementsByTagName(u'Предложение')
    
    for i in itemslist:
        id = i.attributes[u'ИдентификаторТовара'].value
        price = i.attributes[u'Цена'].value

        if Item.has_id_1c(id):
            it = Item.get_by_id_1c(id)
            it.price = float(price)
            it.save()
        else:
            log.append(u'Не обновлена цена для товара с идентификатором %s.'% id)
    log.append(u'Цены для товаров обновлены успешно.')


def go(filename, to_update):
    import os
    filename = os.path.join(settings.PROJECT_ROOT, 'media/' + filename.name)
    xmldoc = minidom.parse(filename)
    log = [u'Начало загрузки из файла %s' % filename]
    if not to_update:
        go_categories(xmldoc, log)
        go_items(xmldoc, log)
    go_prices(xmldoc, log)
    return '\n'.join(log)

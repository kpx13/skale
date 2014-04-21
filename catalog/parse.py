 # -*- coding: utf-8 -*-

import sys
import re
from django.conf import settings
from catalog.models import Category, Item
from xml.dom import minidom

def go_categories(xmldoc):
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
                #print 'SAVED: %s - %s - %s' % (id, name, parent_id)
            #else:
            #    print 'NOTSAVED: %s - %s - %s' % (id, name, parent_id)
        cicle = Category.objects.all().count() > count_a        


def go(filename):
    xmldoc = minidom.parse(filename)
    go_categories(xmldoc)


# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.template import Context, Template

from dashboard import string_with_title
from catalog.models import Item
from users.forms import OrderDataFizForm, OrderDataUrForm
import config
from livesettings import config_value

from django.contrib.sites.models import Site

s = Site.objects.get_current()

DELIVERY_TYPE = (('1', u'Доставка по Москве'),
                 ('2', u'Доставка до ТК'),
                 ('3', u'Доставка до двери за пределами Москвы'),
                 ('4', u'Самовывоз со склада в Москве'),)

def sendmail(subject, body, to_email):
    mail_subject = ''.join(subject)
    send_mail(mail_subject, body, settings.DEFAULT_FROM_EMAIL,
        [to_email])

class Cart(models.Model):
    user = models.ForeignKey(User, verbose_name=u'пользователь')
    item = models.ForeignKey(Item, verbose_name=u'товар')
    count = models.IntegerField(default=1, verbose_name=u'количество')
    date = models.DateTimeField(default=datetime.datetime.now, verbose_name=u'дата добавления')
    
    
    class Meta:
        verbose_name = u'товар в корзине'
        verbose_name_plural = u'товары в корзине'
        ordering = ['-date']
        app_label = string_with_title("shop", u"Магазин")
        
    def __unicode__(self):
        return self.item.name

    
    @staticmethod
    def add_to_cart(user, item, count=1):
        alr = Cart.objects.filter(user=user, item=item)
        if len(alr) == 0:
            Cart(user=user, item=Item.get(item), count=count).save()
        else:
            alr[0].count = alr[0].count + count
            alr[0].save()
    
    @staticmethod     
    def update(user, dict_): 
        for d in dict_:
            Cart(user=user, item=d['item'], count=d['count']).save()
    
    @staticmethod
    def set_count(user, item, count):
        if count <= 0:
            Cart.objects.filter(user=user, item=item).delete()
        else: 
            alr = Cart.objects.filter(user=user, item=item)[0]
            alr.count = count 
            alr.save()
    
    @staticmethod
    def count_plus(user, item):
        alr = Cart.objects.filter(user=user, item=item)[0]
        alr.count += 1 
        alr.save()
            
    
    @staticmethod
    def count_minus(user, item):
        alr = Cart.objects.filter(user=user, item=item)[0]
        if alr.count <= 1:
            alr.delete()
            return
        alr.count -= 1 
        alr.save()
            
    @staticmethod
    def del_from_cart(user, item):
        Cart.objects.filter(user=user, item=item).delete()
    
    @staticmethod    
    def clear(user):
        Cart.objects.filter(user=user).delete()
    
    @staticmethod
    def get_price(cap, item):
        return item.price
    
    @staticmethod
    def get_content(user):
        cart = list(Cart.objects.filter(user=user))
        res = []
        for c in cart:
            res.append({'item': c.item,
                        'count': c.count,
                        'price': Cart.get_price(user, c.item),
                        'sum': Cart.get_price(user, c.item) * c.count})
        return res
    
    @staticmethod
    def present_item(user, item):
        cart = list(Cart.objects.filter(user=user, item=item))
        res = []
        for c in cart:
            res.append({'item': c.item,
                        'count': c.count,
                        'sum': Cart.get_price(user, c.item) * c.count})
        return res
    
    @staticmethod
    def get_count(user, item):
        cart = list(Cart.objects.filter(user=user, item=item))
        if len(cart) > 0:
            return cart[0].count
        else:
            return 0
    
    @staticmethod
    def get_goods_count_and_sum(user):
        try:
            cart = Cart.get_content(user)
            return (sum([x['count'] for x in cart]), sum([x['count'] * Cart.get_price(user, x['item']) for x in cart]))
        except:
            return (0, 0)


class Order(models.Model):
    user = models.ForeignKey(User, verbose_name=u'пользователь')
    date = models.DateTimeField(default=datetime.datetime.now, verbose_name=u'дата заказа')
    comment = models.TextField(blank=True, verbose_name=u'комментарий')
    delivery = models.CharField(choices=DELIVERY_TYPE, max_length=10, verbose_name=u'способ доставки')
    
    class Meta:
        verbose_name = u'заказ'
        verbose_name_plural = u'заказы'
        ordering = ['-date']
        app_label = string_with_title("shop", u"Магазин")
    
    def __unicode__(self):
        return str(self.date)
    
    def get_count(self):
        return sum([x.count for x in OrderContent.get_content(self)])
    
    def get_sum(self):
        return sum([x.count * x.price for x in OrderContent.get_content(self)])
    
    def savecommit(self, *args, **kwargs):
        self.save()
        OrderContent.move_from_cart(self.user, self)
        
        
        profile = self.user.get_profile()
        is_legal=profile.is_legal
        if is_legal:
            module = OrderDataUrForm
        else:
            module = OrderDataFizForm
        orderdata = module(instance=profile.get_orderdata(), initial={'fio': profile.fio})
        
        
        subject=u'Поступил новый заказ.',
        body_templ=u"""
Данные заказчика: 
    {% for f in od.visible_fields %}
        {{ f.label }}: {{ f.value }}
    {% endfor %}

Содержимое:
    {% for c in o.content.all %}
        Ссылка на товар: {{ site }}item/{{ c.item.slug }}/
        {{ c.item.name }}
        Кол-во: {{ c.count }}
        Цена: {{ c.price }} руб.
    {% endfor %}

Общая стоимость:  {{ o.get_sum }} руб.

Комментарий: {{ o.comment }} 
Cпособ доставки: {{ o.get_delivery_display }} 

Ссылка на заказ: {{ site }}admin/shop/order/{{ o.id }}/
"""
        body = Template(body_templ).render(Context({'o': self, 'site': 'http://%s/' % s.domain, 'od': orderdata}))
        sendmail(subject, body, config_value('MyApp', 'EMAIL'))    
        
        subject=u'Вы оформили заказ в магазине %s.' % s.name,
        body_templ=u"""

Содержимое:
    {% for c in o.content.all %}
        Ссылка на товар: {{ site }}item/{{ c.item.slug }}/
        {{ c.item.name }}
        Кол-во: {{ c.count }}
        Цена: {{ c.price }} руб.
    {% endfor %}

Общая стоимость:  {{ o.get_sum }} руб.

Комментарий: {{ o.comment }}
Cпособ доставки: {{ o.get_delivery_display }}

Скоро с Вами свяжется менеджер. Спасибо.
"""
        body = Template(body_templ).render(Context({'o': self, 'site': 'http://%s/' % s.domain}))
        sendmail(subject, body, self.user.email)
                
class OrderContent(models.Model):
    order = models.ForeignKey(Order, verbose_name=u'заказ', related_name='content')
    item = models.ForeignKey(Item, verbose_name=u'товар')
    count = models.IntegerField(default=1, verbose_name=u'количество')
        
    def __unicode__(self):
        return self.item.name
    
    @staticmethod
    def add(order, item, count=None):
        OrderContent(order=order, item=item, count=count).save()
        
    @staticmethod
    def move_from_cart(user, order):
        cart_content = Cart.get_content(user)
        for c in cart_content:
            OrderContent.add(order, c['item'], c['count'])
        Cart.clear(user) 
        
    @staticmethod
    def get_content(order):
        return list(OrderContent.objects.filter(order=order))
    
    @property
    def price(self):
        return self.item.price
    
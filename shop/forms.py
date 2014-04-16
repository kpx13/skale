# -*- coding: utf-8 -*-
 
from django.forms import ModelForm, fields, TextInput
from models import Order
        
class OrderForm(ModelForm):
    class Meta:
        model = Order
        exclude = ('user', 'date')
        
    comment = fields.CharField(widget=TextInput(attrs={'placeholder': u'Комментарий'}))
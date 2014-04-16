# -*- coding: utf-8 -*-
 
from django.forms import ModelForm, Form, fields, PasswordInput
from models import UserProfile, UserOrderDataFiz, UserOrderDataUr
from django.forms.widgets import TextInput
 
class ProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', )
        
        
class RegisterForm(Form):
    fio = fields.CharField(label=u'ФИО')
    is_legal = fields.BooleanField(label=u'Юр лицо?', required=False)
    email = fields.EmailField(label=u'email')
    password_1 = fields.CharField(label=u'пароль 1', widget=PasswordInput)
    password_2 = fields.CharField(label=u'пароль 2', widget=PasswordInput)
    
        
class OrderDataFizForm(ModelForm):
    
    class Meta:
        model = UserOrderDataFiz
        exclude = ('user', )
        fields = ('fio', 'passport', 'address', 'contacts')
    
    fio = fields.CharField(label = u'ФИО', widget=TextInput(attrs={'placeholder': u'ФИО *'}))
    passport = fields.CharField(label = u'Паспортные данные', widget=TextInput(attrs={'placeholder': u'Паспортные данные *'}))
    address = fields.CharField(label = u'Адрес доставки', widget=TextInput(attrs={'placeholder': u'Адрес доставки *'}))
    contacts = fields.CharField(label = u'Контакты', widget=TextInput(attrs={'placeholder': u'Контакты *'}))
    
    
class OrderDataUrForm(ModelForm):
    
    class Meta:
        model = UserOrderDataUr
        exclude = ('user', )
        fields = ('fio', 'inn', 'kpp', 'ur_address', 'address', 'contacts')
    
    fio = fields.CharField(label = u'Название', widget=TextInput(attrs={'placeholder': u'Название *'}))
    inn = fields.CharField(label = u'ИНН', widget=TextInput(attrs={'placeholder': u'ИНН *'}))
    kpp = fields.CharField(label = u'КПП', widget=TextInput(attrs={'placeholder': u'КПП *'}))
    ur_address = fields.CharField(label = u'Юридический адрес', widget=TextInput(attrs={'placeholder': u'Юридический адрес *'}))
    address = fields.CharField(label = u'Адрес доставки', widget=TextInput(attrs={'placeholder': u'Адрес доставки *'}))
    contacts = fields.CharField(label = u'Контакты', widget=TextInput(attrs={'placeholder': u'Контакты *'}))
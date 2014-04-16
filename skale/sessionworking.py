# -*- coding: utf-8 -*-

from catalog.models import Item


class SessionCartWorking(object):
    def __init__(self, request):
        self.__request = request
        
    def var(self, item):
        return  '_'.join(['cart', str(item)])
        
    def add_to_cart(self, cap, item, count=1):
        if self.var(item) in self.__request.session.keys():
            self.__request.session[self.var(item)] += count 
        else:
            self.__request.session[self.var(item)] = count
    
    def del_from_cart(self, cap, item):
	    del self.__request.session[self.var(item)]
        
    def get_count(self, cap, item):
        return self.__request.session[self.var(item)]
    
    def get_price(self, cap, item):
        opt = cap.is_authenticated() and cap.get_profile().is_opt
        if opt: 
            return item.price_opt
        else:
            return item.price
    
    def get_content(self, cap):
        res = []
        
        for i in self.__request.session.keys():
            if i.startswith('cart_'):
                item = i[5:]
                item = Item.get(int(item))
                res.append({'item': item,
                            'count': int(self.__request.session[i]),
                            'price': self.get_price(cap, item),
                            'sum': int(self.__request.session[i]) * self.get_price(cap, item)})
        return res
    
    def present_item(self, cap, item):
        res = []
        for i in self.__request.session.keys():
            if i.startswith('cart_' + str(item)):
                item = i[5:]
                item = Item.get(int(item))
                res.append({'item': item,
                            'count': int(self.__request.session[i]),
                            'sum': int(self.__request.session[i]) * self.get_price(cap, item)})
        return res
    
    def pop_content(self):
        res = []
        for i in self.__request.session.keys():
            if i.startswith('cart_'):
                item = i[5:]
                res.append({'item': Item.get(int(item)),
                            'count': int(self.__request.session[i])})
                del self.__request.session[i]
        return res
    
    def get_goods_count_and_sum(self, cap):
        cart = self.get_content(cap)
        return (sum([x['count'] for x in cart]), sum([x['count'] * self.get_price(cap, x['item']) for x in cart]))
    
    def count_plus(self, cap, item):
        self.__request.session[self.var(item)] += 1
        
    def count_minus(self, cap, item):
        if self.__request.session[self.var(item)] <= 1:
            self.del_from_cart(cap, item)
        else:
            self.__request.session[self.var(item)] -= 1
            
    def set_count(self, cap, item, count):
        count= int(count)
        
        if count <= 0:
            self.del_from_cart(cap, item)
        else:
            self.__request.session[self.var(item)] = count
    
    

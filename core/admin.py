from django.contrib import admin
from .models import Item, OrderItem, Order, Contact, Coupon, Payment

# Register your models here.



admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(Item)
admin.site.register(Coupon)
admin.site.register(Contact)


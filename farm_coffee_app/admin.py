from django.contrib import admin

from farm_coffee_app.models import Product, Total_Order, Order_Product
from django.contrib import admin
# Register your models here.

admin.site.register(Product)
admin.site.register(Total_Order)
admin.site.register(Order_Product)
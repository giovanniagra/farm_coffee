from django.contrib import admin

from farm_coffee_app.models import Product, Review, Total_Order, Order_Product, Topping
from django.contrib import admin
# Register your models here.

admin.site.register(Product)
admin.site.register(Total_Order)
admin.site.register(Order_Product)
admin.site.register(Review)
admin.site.register(Topping)

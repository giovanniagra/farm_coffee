from django.contrib import admin

from farm_coffee_app.models import Product, Review, Total_Order, Cart, Topping
from django.contrib import admin
# Register your models here.

admin.site.register(Product)
admin.site.register(Total_Order)
admin.site.register(Cart)
admin.site.register(Review)
admin.site.register(Topping)

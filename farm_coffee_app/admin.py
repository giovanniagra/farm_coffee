from django.contrib import admin

from farm_coffee_app.models import Order, Product, Review, Cart, Topping
from django.contrib import admin
# Register your models here.

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(Review)
admin.site.register(Topping)


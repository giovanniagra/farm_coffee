from asyncio.windows_events import NULL
from distutils.command.upload import upload
from email.policy import default
from msilib.schema import AdminExecuteSequence
from django.db import models
from django.contrib.auth.models import User, Group


from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.forms import JSONField
from django.utils import timezone
import datetime
from django.conf import settings
from django.shortcuts import reverse
from django.db.models.deletion import CASCADE, SET_NULL
from django.contrib.auth.models import Group

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    # street = models.CharField(max_length=255)
    # city = models.CharField(max_length=255)
    # province = models.CharField(max_length=255)
    # zip_code = models.CharField(max_length=255)
    
    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    phone_number = models.CharField(validators = [phoneNumberRegex], max_length=16)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            group = Group.objects.get(name='Customer')
            group.user_set.add(instance)
            Profile.objects.create(user=instance)
            Cart.objects.create(user=instance.profile)

    # @receiver(post_save, sender=User)
    # def save_user_profile(sender, instance, **kwargs):
    #     instance.profile.save()
    #     Cart.objects.create(user=instance.profile)

    # @receiver(post_save, sender=User)
    # def create_user_cart(sender, instance, created, **kwargs):
    #     if created:
            

# Automation to create cart once a user instance is created.


class Product(models.Model):
    # BOBA = 'B'
    # WHIPPED_CREAM = 'WC'
    # COFFEE_SHOT = 'CS'
    # TOPPING_CHOICES = (
    #     (BOBA,'Boba'),
    #     (WHIPPED_CREAM,'Whipped Cream'),
    #     (COFFEE_SHOT,'Coffee Shot'),
    # )
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, null=True, blank=True)
    # type = models.CharField(max_length=255, null=True, blank=True)
    # topping_choices = models.CharField(max_length=2, choices=TOPPING_CHOICES)
    price = models.FloatField()
    # topping_price = models.FloatField()
    image = models.ImageField(upload_to='product_images', default='default.jpg')
    availability = models.BooleanField()
    pub_date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
       return f"{self.product_id}: {self.name}"

    def get_absolute_url(self):
        return reverse("farm_coffee_app:read_product_detail", kwargs={
            "pk" : self.pk
        })

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Order(models.Model):
    ORDERING = 'ORD'
    PREPARING = 'PRE'
    DELIVERING = 'DEL'
    DELIVERED = 'DED'
    STATUS_NAMES = (
        (ORDERING,'Ordering'),
        (PREPARING,'Preparing'),
        (DELIVERING,'Delivering'),
        (DELIVERED, 'Delivered'),
    )
    order_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=50, choices=STATUS_NAMES, default=ORDERING)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=150, null=False)
    last_name = models.CharField(max_length=150, null=False)
    street = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    province = models.CharField(max_length=150)
    zip_code = models.CharField(max_length=150)
    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    phone_number = models.CharField(validators = [phoneNumberRegex], max_length=16)
    order_created_time = models.DateTimeField(null=True, blank=True)
    time_of_delivery = models.DateTimeField(null=True, blank=True)
    delivery_completion = models.DateTimeField(null=True, blank=True)
    payment_received = models.BooleanField(null=True, blank=True)
    # detail = JSONField("order_detail")  #has details about those products

    def __str__(self):
        return f"{self.order_id} {self.status_name} {self.user}"

    # @property
    # def get_cart_total(self):
    #     orderitems = self.cart_set.all()
    #     total = sum([item.get_total for item in orderitems])
    #     return total 
    
    # @property
    # def get_cart_items(self):
    #     orderitems = self.cart_set.all()
    #     total = sum([item.quantity for item in orderitems])
    #     return total
        

class Cart(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    # order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cart of {self.user.user}'

    @property
    def get_total(self):
        total = 0
        items = Cart.objects.filter(user=self.user).values('quantity')
        for item in items:
            total += item['quantity']
        return total

    @property
    def get_total_price(self):
        price = 0
        items = Cart.objects.filter(user=self.user)
        for item in items:
            price += item.product.price * item.quantity
        return price

class Review(models.Model):
    reviews_id = models.AutoField(primary_key=True)
    users_fk_user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    product_fk_product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='review')
    rating = models.FloatField()
    review_description = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f"{self.reviews_id} {self.review_description}"


# class Payment_Proof(models.Model):

#     users_fk_user_id = models.ForeignKey(User, on_delete=models.CASCADE)
#     total_order_fk_order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
#     address_fk_address_id = models.ForeignKey(Profile, on_delete=models.CASCADE)


class Item(models.Model):
    order = models.ForeignKey(Order, on_delete=CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=SET_NULL, null=True)

    def __str__(self):
        return f'{self.order.user} ordered {self.product.name}'

class Quantity(models.Model):
    item = models.OneToOneField(Item, on_delete=CASCADE, null=True)
    quantity = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.item.product.name} Quantity = {str(self.quantity)}"
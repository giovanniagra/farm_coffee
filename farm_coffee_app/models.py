from asyncio.windows_events import NULL
from distutils.command.upload import upload
from msilib.schema import AdminExecuteSequence
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
import datetime
from django.conf import settings
from django.shortcuts import reverse


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)
    
    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    phone_number = models.CharField(validators = [phoneNumberRegex], max_length=16)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

class Role(models.Model):
    ADMIN = 'Adm'
    EMPLOYEE = 'Emp'
    CUSTOMER = 'Cus'
    ROLE_NAMES = (
        (ADMIN, 'Admin'),
        (EMPLOYEE, 'Employee'),
        (CUSTOMER, 'Customer'),
    )
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=10, choices=ROLE_NAMES)

# class users(models.Model):
#     user_id = models.IntegerField(primary_key=True)
#     address_fk_address_id = models.ForeignKey(address, on_delete=models.CASCADE)
#     role_fk_role_id = models.ForeignKey(Role, on_delete=models.CASCADE)
#     email = models.CharField(max_length=255)
#     first_name = models.CharField(max_length=255)
#     last_name = models.CharField(max_length=255)
#     password = models.CharField(max_length=255)

class Order_Status(models.Model):
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
    status_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=50, choices=STATUS_NAMES)

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.FloatField()
    image = models.ImageField(upload_to='images/', default='default.jpg')
    availability = models.BooleanField()
    pub_date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
       return f"{self.product_id}: {self.name}"

    def get_absolute_url(self):
        return reverse("farm_coffee_app:read_product_detail", kwargs={
            "pk" : self.pk
        })

    def get_add_to_car_url(self):
        return reverse("farm_coffee_app:add_to_cart", kwargs={
            "pk" : self.pk
        })

    def get_remove_from_cart_url(self) :
        return reverse("farm_coffee_app:remove_from_cart", kwargs={
            "pk" : self.pk
        })

class Topping(models.Model):
    toppings_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.FloatField()
    availability = models.BooleanField()

class Review(models.Model):
    reviews_id = models.AutoField(primary_key=True)
    users_fk_user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    product_fk_product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='review')
    rating = models.FloatField()
    review_description = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f"{self.reviews_id} {self.review_description}"

class Order_Product(models.Model):
    order_product_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product_fk_product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    toppings_fk_toppings_id = models.ForeignKey(Topping , on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    order_product_quantity = models.IntegerField(default=1)
    order_topping_quantity = models.IntegerField()

    def __str__(self):
        return f"{self.order_product_quantity} of {self.product_fk_product_id.Product.name}"

class Total_Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # order_status_fk_status_id = models.OneToOneField(Order_Status, on_delete=models.CASCADE)
    order_product_fk_order_product_id = models.ManyToManyField(Order_Product)
    order_created_time = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    time_of_delivery = models.DateTimeField()
    delivery_completion = models.DateTimeField()
    payment_received = models.BooleanField()

    def __str__(self):
        return self.user.username

class Payment_Proof(models.Model):

    users_fk_user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    total_order_fk_order_id = models.ForeignKey(Total_Order, on_delete=models.CASCADE)
    address_fk_address_id = models.ForeignKey(Profile, on_delete=models.CASCADE)

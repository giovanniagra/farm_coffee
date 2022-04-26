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

class role(models.Model):
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
#     role_fk_role_id = models.ForeignKey(role, on_delete=models.CASCADE)
#     email = models.CharField(max_length=255)
#     first_name = models.CharField(max_length=255)
#     last_name = models.CharField(max_length=255)
#     password = models.CharField(max_length=255)

class order_status(models.Model):
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

class total_order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user_fk_user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    order_status_fk_status_id = models.ForeignKey(order_status, on_delete=models.CASCADE)
    order_created_time = models.DateTimeField()
    time_of_delivery = models.DateTimeField()
    delivery_completion = models.DateTimeField()
    payment_received = models.BooleanField()
    price = models.DecimalField(decimal_places=2, max_digits=10)

class payment_proof(models.Model):

    users_fk_user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    total_order_fk_order_id = models.ForeignKey(total_order, on_delete=models.CASCADE)
    address_fk_address_id = models.ForeignKey(Profile, on_delete=models.CASCADE)

class products(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    image = models.ImageField(upload_to='images/', default='default.jpg')
    availability = models.BooleanField()
    pub_date = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return "{}".format(self.product_id)

class toppings(models.Model):
    toppings_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    availability = models.BooleanField()

class reviews(models.Model):
    reviews_id = models.AutoField(primary_key=True)
    users_fk_user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    products_fk_products_id = models.ForeignKey(products, on_delete=models.CASCADE)
    rating = models.IntegerField()
    review_description = models.TextField()

class order_product(models.Model):
    order_product_id = models.AutoField(primary_key=True)
    total_order_fk_order_id = models.ForeignKey(total_order, on_delete=models.CASCADE)
    products_fk_product_id = models.ForeignKey(products, on_delete=models.CASCADE)
    toppings_fk_toppings_id = models.ForeignKey(toppings , on_delete=models.CASCADE)
    order_product_quantity = models.IntegerField()
    order_topping_quantity = models.IntegerField()


    
    

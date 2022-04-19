from msilib.schema import AdminExecuteSequence
from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class address(models.Model):
    address_id = models.IntegerField(primary_key=True)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)

class role(models.Model):
    ADMIN = 'Adm'
    EMPLOYEE = 'Emp'
    CUSTOMER = 'Cus'
    ROLE_NAMES = (
        (ADMIN, 'Admin'),
        (EMPLOYEE, 'Employee'),
        (CUSTOMER, 'Customer'),
    )
    role_id = models.IntegerField(primary_key=True)
    role_name = models.CharField(max_length=10, choices=ROLE_NAMES)

class users(models.Model):
    user_id = models.IntegerField(primary_key=True)
    address_fk_address_id = models.ForeignKey(address, on_delete=models.CASCADE)
    role_fk_role_id = models.ForeignKey(role, on_delete=models.CASCADE)
    email = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

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
    status_id = models.IntegerField(primary_key=True)
    status_name = models.CharField(max_length=50, choices=STATUS_NAMES)

class total_order(models.Model):
    order_id = models.IntegerField(primary_key=True)
    user_fk_user_id = models.ForeignKey(users, on_delete=models.CASCADE)
    order_status_fk_status_id = models.ForeignKey(order_status, on_delete=models.CASCADE)
    order_created_time = models.DateTimeField()
    time_of_delivery = models.DateTimeField()
    delivery_completion = models.DateTimeField()
    payment_received = models.BooleanField()
    price = models.DecimalField(decimal_places=2, max_digits=10)

class payment_proof(models.Model):

    users_fk_user_id = models.ForeignKey(users, on_delete=models.CASCADE)
    total_order_fk_order_id = models.ForeignKey(total_order, on_delete=models.CASCADE)
    address_fk_address_id = models.ForeignKey(address, on_delete=models.CASCADE)

class products(models.Model):
    product_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    availability = models.BooleanField()

class toppings(models.Model):
    toppings_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    availability = models.BooleanField()

class reviews(models.Model):
    reviews_id = models.IntegerField(primary_key=True)
    users_fk_user_id = models.ForeignKey(users, on_delete=models.CASCADE)
    products_fk_products_id = models.ForeignKey(products, on_delete=models.CASCADE)
    rating = models.IntegerField()
    review_description = models.TextField()

class order_product(models.Model):
    order_product_id = models.IntegerField(primary_key=True)
    total_order_fk_order_id = models.ForeignKey(total_order, on_delete=models.CASCADE)
    products_fk_product_id = models.ForeignKey(products, on_delete=models.CASCADE)
    toppings_fk_toppings_id = models.ForeignKey(toppings , on_delete=models.CASCADE)
    order_product_quantity = models.IntegerField()
    order_topping_quantity = models.IntegerField()


    
    

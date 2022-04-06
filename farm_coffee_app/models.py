from django.db import models

# Create your models here.

class users(models.Model):
    user_id = models.IntegerField(primary_key=True)
    address_fk__address_id = models.ForeignKey()
    role_fk_role_id = models.ForeignKey()
    email = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

class address(models.Model):
    address_id = models.IntegerField(primary_key=True)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=255)

class role(models.Model):
    ROLE_NAMES = (
        ('Admin'),
        ('Employee'),
        ('Customer'),
    )
    role_id = models.IntegerField(primary_key=True)
    role_name = models.CharField(max_length=10, choices=ROLE_NAMES, default='Customer')

class total_order(models.Model):
    order_id = models.IntegerField(primary_key=True)
    user_fk_user_id = models.ForeignKey()
    order_status_fk_status_id = models.ForeignKey()
    order_created_time = models.DateTimeField()
    time_of_delivery = models.DateTimeField()
    delivery_completion = models.DateTimeField()
    payment_received = models.BooleanField()
    price = models.DecimalField()

class payment_proof(models.Model):

    users_fk_user_id = models.ForeignKey()
    total_order_fk_order_id = models.ForeignKey()
    address_fk_address_id = models.ForeignKey()

class reviews(models.Model):
    reviews_id = models.IntegerField(primary_key=True)
    users_fk_user_id = models.ForeignKey()
    products_fk_products_id = models.ForeignKey()
    rating = models.IntegerField()
    review_description = models.TextField()

class order_status(models.Model):
    STATUS_NAMES = (
        ('Ordering'),
        ('Preparing'),
        ('Delivering'),
        ('Delivered'),
    )
    status_id = models.IntegerField(primary_key=True)
    status_name = models.CharField(max_length=255, choices=STATUS_NAMES)

class order_product(models.Model):
    order_product_id = models.IntegerField(primary_key=True)
    total_order_fk_order_id = models.ForeignKey()
    products_fk_product_id = models.ForeignKey()
    toppings_fk_toppings_id = models.ForeignKey()
    order_product_quantity = models.IntegerField()
    order_topping_quantity = models.IntegerField()

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
    
    

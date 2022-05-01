# Generated by Django 3.2.3 on 2022-04-28 09:10

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order_Product',
            fields=[
                ('order_product_id', models.AutoField(primary_key=True, serialize=False)),
                ('ordered', models.BooleanField(default=False)),
                ('order_product_quantity', models.IntegerField(default=1)),
                ('order_topping_quantity', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Order_Status',
            fields=[
                ('status_id', models.AutoField(primary_key=True, serialize=False)),
                ('status_name', models.CharField(choices=[('ORD', 'Ordering'), ('PRE', 'Preparing'), ('DEL', 'Delivering'), ('DED', 'Delivered')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('product_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('price', models.FloatField()),
                ('image', models.ImageField(default='default.jpg', upload_to='images/')),
                ('availability', models.BooleanField()),
                ('pub_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('role_id', models.AutoField(primary_key=True, serialize=False)),
                ('role_name', models.CharField(choices=[('Adm', 'Admin'), ('Emp', 'Employee'), ('Cus', 'Customer')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Topping',
            fields=[
                ('toppings_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('price', models.FloatField()),
                ('availability', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Total_Order',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('order_created_time', models.DateTimeField()),
                ('ordered', models.BooleanField(default=False)),
                ('time_of_delivery', models.DateTimeField()),
                ('delivery_completion', models.DateTimeField()),
                ('payment_received', models.BooleanField()),
                ('order_product_fk_order_product_id', models.ManyToManyField(to='farm_coffee_app.Order_Product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('reviews_id', models.AutoField(primary_key=True, serialize=False)),
                ('rating', models.FloatField()),
                ('review_description', models.TextField()),
                ('product_fk_product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='farm_coffee_app.product')),
                ('users_fk_user_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('province', models.CharField(max_length=255)),
                ('zip_code', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=16, validators=[django.core.validators.RegexValidator(regex='^\\+?1?\\d{8,15}$')])),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment_Proof',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_fk_address_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='farm_coffee_app.profile')),
                ('total_order_fk_order_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='farm_coffee_app.total_order')),
                ('users_fk_user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='order_product',
            name='product_fk_product_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='farm_coffee_app.product'),
        ),
        migrations.AddField(
            model_name='order_product',
            name='toppings_fk_toppings_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='farm_coffee_app.topping'),
        ),
        migrations.AddField(
            model_name='order_product',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
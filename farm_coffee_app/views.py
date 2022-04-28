from multiprocessing import context
from pyexpat import model
from re import template
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from pytz import timezone
from .forms import ProductForm, SignUpForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.views import generic
from .forms import *
from .models import Product, Profile, Review, Total_Order, Order_Product
import traceback
from datetime import datetime
from django.contrib.auth.decorators import login_required




# Create your views here.

# Sign-Up, Log-In, and Password-reset
def home(request):
    return render(request, 'home.html', {})

def menu(request):
    return render(request, 'menu.html', {})

def register_request(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"New account created: {username}")
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        else:
            messages.error(request, "Account creation failed")

        return redirect("farm_coffee_app:home")
    form = SignUpForm()
    return render(request, "register.html", {"form": form})

def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("farm_coffee_app:home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="login.html", context={"login_form":form})

def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("farm_coffee_app:home")

def user_details(request, user_id):
    return HttpResponse("User details %s" % user_id)

def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "password/password_reset_email.txt"
                    c = {
                        "email":user.email,
                        'domain':'127.0.0.1:8000',
                        'site_name': 'Farm Coffee',
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'admin@fcoffee.com', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect ("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="password/password_reset.html", context={"password_reset_form":password_reset_form})

#Profile CRUD

def profilepage(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, ('Your profile was successfully updated!'))
            return redirect('farm_coffee_app:profilepage')
        else:
            messages.error(request, ('Please correct the errors below.'))
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'profile_page.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

# Add to Cart Function
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    order_product, created = Order_Product.objects.get_or_create(
        product_fk_product_id=product_fk_product_id,
        user = request.user,
        ordered = False
    )
    ordering = Total_Order.objects.filter(user=request.user, ordered=False)

    if ordering.exists():
        order = ordering[0]

        if order.items.filter(product__pk = product.pk).exists():
            order_product.order_product_quantity += 1
            order_product.save()
            messages.info(request, "Added Product")
            return redirect("core:product", pk = pk)
        else:
            Total_Order.order_product_fk_order_product_id.add(order_product)
            messages.info(request, "Product added to your cart")
            return redirect("core:product", pk = pk)
    else:
        order_created_time = timezone.now()
        order = Total_Order.objects.create(user=request.user, order_created_time=order_created_time)
        Order_Product.order_product_quantity.add(order_item)
        messages.info(request, "Product add to your cart")
        return redirect ("core:product", pk = pk)

# Remove From Cart Function
def remove_from_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    ordering = Total_Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if ordering.exists():
        order = ordering_qs[0]
        if order.items.filter(product__pk = product.pk).exists():
            order_product = Order_Product.objects.filter(
                product_fk_product_id = product_fk_product_id,
                user = request.user,
                ordered = False
            )[0]
            order_product.delete()
            messages.info(request, "Product \""+order_product.product_fk_product_id.name+"\" removed from your cart")
            return redirect("core:product")
        else:
            messages.info(request, "This product is not in your cart")
            return redirect("core:product", pk=pk)
    else:
        messages.info(request, "You do not have an Order")
        return redirect("core:product", pk = pk)

#Manage Order CRD

# class create_order(generic.CreateView):
#     model = Total_Order
#     template_name = 'order/total_order_form.html'
#     form_class= TotalOrderForm

#     def form_valid(self, form):
#         print("super", super().form_valid(form),)
#         return super().form_valid(form)

# class read_order(generic.DetailView):
# class read_order_list(generic.ListView):
# class delete_order(generic.DeleteView):

#Product CRUD

class create_product(generic.CreateView):
    model = Product
    template_name = 'product/product_form.html'
    form_class = ProductForm
    success_url = '/' 
    
    def form_valid(self, form):
        print("super", super().form_valid(form),)
        return super().form_valid(form)

class read_product_list(generic.ListView):
    template_name = 'product/read_product_list.html'
    context_object_name = 'view_product_list'

    def get_queryset(self):
        return Product.objects.filter(pub_date__lte=datetime.now()).order_by('-pub_date')

class read_product_detail(generic.DetailView):
    model = Product
    template_name = 'product/read_product_detail.html'

class update_product(generic.UpdateView):
    model = Product
    fields = ['name', 'price', 'image', 'availability']
    template_name= 'product/update_product.html'
    success_url = '/details/{product_id}'
    def get_object(self, queryset=None):
        id = self.kwargs.get('pk')
        return get_object_or_404(Product, product_id=id)

class delete_product(generic.DeleteView):
    model = Product
    template_name = 'product/confirm_delete_product.html'
    success_url = '/'

#Topping CRUD
# class create_topping(generic.CreateView):
# class read_topping(generic.DetailView):
# class read_topping_list(generic.ListView):
# class update_topping(generic.UpdateView):
# class delete_topping(generic.DeleteView):

#Review CRUD
class create_review(generic.CreateView):
    model = Review
    template_name = 'review/review_form.html'
    form_class = ReviewForm
    success_url = '/'
    

# class read_review(generic.DetailView):
# class read_review_list(generic.ListView):
# class update_review(generic.UpdateView):
# class delete_review(generic.DeleteView):
    
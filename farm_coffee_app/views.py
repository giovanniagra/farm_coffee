from multiprocessing import context
from pyexpat import model
from django.http import HttpResponse
from django.shortcuts import render, redirect
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
from .forms import ProductForm, UserForm, ProfileForm
from .models import products





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
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)
    return render(request=request, template_name="profile_page.html", context={"user":request.user, "user_form":user_form, "profile_form":profile_form})

#Manage Order CRD

# class create_order(generic.CreateView):
# class read_order(generic.DetailView):
# class read_order_list(generic.ListView):
# class delete_order(generic.DeleteView):

#Product CRUD

class create_product(generic.CreateView):
    model = products
    template_name = 'product/product_form.html'
    form_class = ProductForm
    success_url = '/'

# class read_product(generic.DetailView):
#     model = products
#     template_name = 'farm_coffee_app/read_product.html'

# class read_product_list(generic.ListView):
#     template_name = 'farm_coffee_app/.html'
    
# class update_product(generic.UpdateView):

# class delete_product(generic.DeleteView):

#Delivery CRUD
# class create_delivery(generic.CreateView):
# class read_delivery(generic.DetailView):
# class read_delivery_list(generic.ListView):
# class update_delivery(generic.UpdateView):
# class delete_delivery(generic.DeleteView):

#Review CRUD
# class create_review(generic.CreateView):
# class read_review(generic.DetailView):
# class read_review_list(generic.ListView):
# class update_review(generic.UpdateView):
# class delete_review(generic.DeleteView):
    
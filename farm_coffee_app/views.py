from asyncio import proactor_events
from itertools import chain
from multiprocessing import context
from pyexpat import model
from re import template
from sqlite3 import complete_statement
from urllib.request import ProxyDigestAuthHandler
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from numpy import product
from pytz import timezone
from .forms import ProductForm, SignUpForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages, auth
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, UserCreationForm
from django.core.mail import EmailMessage, send_mail
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.views import generic, View
from .forms import UserForm, ProfileForm
from .models import Product, Profile, Review, Order, Cart
import traceback
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
import json
# from .utils import account_activation_token



# Create your views here.

# Recommendation Engine
def recommendation_engine(request):

    reviews =  Review.objects.all()
    products = Product.objects.all()
    x,y,A,B = []
    
    for product in products:
        x=[product.product_id, product.name,product.price,product.image]
        y+=[x]
    products_df = pd.DataFrame(y,columns=['productId','title','price','image'])
    
    
    for review in reviews:
        A = [review.users_fk_user_id.pk, review.product_fk_product_id.pk, review.rating]
        B+=[A]
    
    rating_df = pd.DataFrame(B, columns=['userId', 'productId', 'rating'])
    rating_df['userId']=rating_df['userId'].astype(str).astype(np.int64)
    rating_df['productId']=rating_df['productId'].astype(str).astype(np.int64)
    # rating_df['rating']=rating_df['rating'].astype(str).astype(np.float)

    reviews2 = pd.merge(rating_df, products_df, how='inner', on='productId')

    current_user = request.user
    user = current_user.id

    df = reviews2.pivot_table(index='productId',columns='userId',values='rating').fillna(0)
    df1 = df.copy()

    num_neighbors = 10
    num_recommendation = 10
    
    number_neighbors = num_neighbors
    
    knn = NearestNeighbors(metric='cosine', algorithm='brute')
    knn.fit(df.values)
    distances, indices = knn.kneighbors(df.values, n_neighbors=number_neighbors)
    
    user_index = df.columns.tolist().index(user)
    
    for p,t in list(enumerate(df.index)):
        if df.iloc[p, user_index] == 0:
            sim_products = indices[p].tolist()
            product_distances = distances[p].tolist()
            
            if p in sim_products:
                id_product = sim_products.index(p)
                sim_products.remove(p)
                product_distances.pop(id_product)
                
            else:
                sim_products = sim_products[:num_neighbors-1]
                product_distances = product_distances[:num_neighbors-1]
                
            product_similarity = [1-x for x in product_distances]
            product_similarity_copy = product_similarity.copy()
            nominator = 0
            
            for s in range(0, len(product_similarity)):
                if df.iloc[sim_products[s], user_index] == 0:
                    if len(product_similarity_copy) == (number_neighbors - 1):
                        product_similarity_copy.pop(s)
                        
                    else:
                        product_similarity_copy.pop(s-(len(product_similarity)-len(product_similarity_copy)))
                        
                else:
                    nominator = nominator + product_similarity[s]*df.iloc[sim_products[s],user_index]
                    
            if len(product_similarity_copy) > 0:
                if sum(product_similarity_copy) > 0:
                    predicted_r = nominator/sum(product_similarity_copy)
                    
                else:
                    predicted_r = 0
                    
            else:
                predicted_r = 0
                
            df1.iloc[p,user_index] = predicted_r
    
    recommended_products = []

    for m in df[df[user] == 0].index.tolist():
        index_df = df.index.tolist().index(m)
        predicted_rating = df1.iloc[index_df, df1.columns.tolist().index(user)]
        recommended_products.append((m, predicted_rating))

    sorted_rm = sorted(recommended_products, key=lambda x:x[1], reverse=True)
     
    set = sorted_rm[:num_recommendation]
    set = [ x[0] for x in set]

    recommendations = Product.objects.filter(product_id__in=set)
    
    return recommendations
    

# @login_required(login_url='login')
def home(request):
    products = Product.objects.filter(pub_date__lte=datetime.now()).order_by('-pub_date')[0:4]
    return render(request, 'home.html', {"products": products})

#Profile CRUD
@login_required(login_url='farm_coffee_app:login')
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


#Product CRUD
class create_product(LoginRequiredMixin, generic.CreateView):
    model = Product
    template_name = 'product/product_form.html'
    form_class = ProductForm
    success_url = '/list' 

    def get_context_data(self, **kwargs):
        ctx = super(create_product, self).get_context_data(**kwargs)
        prods = Product.objects.all()
        cates = []
        for prod in prods:
            if prod.category is not None and not prod.category in cates:
                cates.append(prod.category)
        ctx["cates"] = cates
        return ctx

    def form_valid(self, form):
        
        print("super", super().form_valid(form),)
        return super().form_valid(form)

class read_product_list(LoginRequiredMixin, generic.ListView):
    template_name = 'product/read_product_list.html'
    context_object_name = 'view_product_list'

    def get_queryset(self):
        return Product.objects.filter(pub_date__lte=datetime.now()).order_by('-pub_date')

# Displays the menu
class menu( generic.ListView):
    template_name = 'menu.html'
    context_object_name = 'view_product_list'

    def get_queryset(self):
        return Product.objects.filter(pub_date__lte=datetime.now()).order_by('-pub_date')
        

class read_product_detail(generic.DetailView):
    model = Product
    template_name = 'product/read_product_detail.html'
    
    def get_queryset(self):
        return Product.objects.filter(pub_date__lte=datetime.now()).order_by('-pub_date')


class update_product(LoginRequiredMixin, generic.UpdateView):
    model = Product
    fields = ['name', 'price', 'image', 'availability']
    template_name= 'product/update_product.html'
    success_url = '/details/{product_id}'
    def get_object(self, queryset=None):
        id = self.kwargs.get('pk')
        return get_object_or_404(Product, product_id=id)

class delete_product(LoginRequiredMixin, generic.DeleteView):
    model = Product
    template_name = 'product/confirm_delete_product.html'
    success_url = '/list'

# Functions dealing with Reviews
@login_required(login_url='farm_coffee_app:login')
def create_review(request):
    product_fk_product_id=request.POST['product_fk_product_id']
    print(request.user)
    review=Review(
        users_fk_user_id=request.user,
        product_fk_product_id=Product.objects.get(product_id=product_fk_product_id),
        rating=request.POST['rating'],
        review_description= request.POST['review_description'])
    review.save()

    messages.success(request, "review has been created")
    return HttpResponseRedirect(reverse('farm_coffee_app:read_product_list'))
     

class read_review(LoginRequiredMixin, generic.ListView):
    template_name = 'product/read_product_detail.html'
    context_object_name = 'view_reviews'

    def get_queryset(self):
        return Review.objects.all()

class update_review(LoginRequiredMixin, generic.UpdateView):
    model = Review
    fields = ['rating', 'review_description']
    template_name= 'review/update_review.html'
    success_url = '/list'
    # success_url = '/details/{product_fk_product_id}'
    # def get_object(self, queryset=None):
    #     id = self.kwargs.get('pk')
    #     return get_object_or_404(Review, product_fk_product_id=id)

class delete_review(LoginRequiredMixin, generic.DeleteView):
    model = Review
    template_name = 'review/confirm_delete_review.html'
    success_url = '/list'

# Functions dealing with the cart logic  
@login_required(login_url='farm_coffee_app:login')
def cart(request):
    try:
        order = Order.objects.get(user=request.user)
    except Order.DoesNotExist:
        messages.debug(request, "Can't access cart. Try to add on of our items!")
        return redirect('farm_coffee_app:read_product_list')

    # order = order.first()
    items = Cart.objects.filter(order=order).order_by('-date_added')
    context = {'items':items, 'order':order}
    return render(request, 'cart/cart.html', context)
  
# Functions dealing with checkout logic
@login_required(login_url='farm_coffee_app:login')
def checkout(request):
    form_details = ProfileForm()
    form_name = UserForm()

    order = Order.objects.get(user=request.user)
    items = Cart.objects.filter(order=order).order_by('-date_added')
    context = {'items':items, 'order':order, 'form_details':form_details, 'form_name':form_name}
    return render(request, 'checkout/checkout.html', context)

# @login_required(login_url='farm_coffee_app:login')
def update_item(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user
    product = Product.objects.get(product_id=productId)
    order, created = Order.objects.get_or_create(user=customer, payment_received=False)

    cart, created = Cart.objects.get_or_create(order=order, product=product)

    if action == 'add':
        cart.quantity = (cart.quantity + 1)
    elif action == 'remove':
        cart.quantity = (cart.quantity - 1)
    
    cart.save()

    if cart.quantity <= 0:
        cart.delete()
    return JsonResponse('Item was added', safe=False)

@login_required(login_url='farm_coffee_app:login')
def placeorder(request):
    if request.method == 'POST':
        neworder = Order()
        neworder.user = request.user
        neworder.first_name = request.POST.get('first_name')
        neworder.last_name = request.POST.get('last_name')
        neworder.street = request.POST.get('street')
        neworder.city = request.POST.get('city')
        neworder.province = request.POST.get('province')
        neworder.zip_code = request.POST.get('zip_code')
        neworder.phone_number = request.POST.get('phone_number')

        neworder.total_price = Order.get_cart_total()
        neworder.save

        neworderitems = Cart.objects.filter(user=request.user)
        for item in neworderitems:
            Cart.objects.create(
                order=neworder,
                product=item.product,
                price=item.product.price
            )
        
        Cart.objects.filter(user=request.user).delete()

        messages.success(request, "Your order has been received! We will be working on it as soon as possible!")

        return redirect('')

def recommendation_page(request):
    recommendations=recommendation_engine(request)
    
    return render(request, "recommendations/recommendation.html", {'recommended':recommendations})
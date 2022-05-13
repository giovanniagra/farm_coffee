from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from sklearn.neighbors import NearestNeighbors
from .forms import ProductForm, OrderForm
from django.contrib import messages
from django.views import generic
from django.urls import reverse
from datetime import datetime
from django.db.models import F
from django.contrib.auth.models import User, Group
from .models import Profile, Product, Order, Cart, Review, Item, Quantity
from .forms import EmployeeForm, UserForm, ProfileForm, ProductForm, OrderForm, ReviewForm
import pandas as pd
import numpy as np
import json




#group checking 
def is_manager(user):
    return (user.groups.filter(name="Manager").exists())

def is_employee(user):
    return (user.groups.filter(name="Employee").exists())

# Recommendation Engine
def recommendation_engine(request):

    reviews =  Review.objects.all()
    products = Product.objects.all()
    x,y,A,B = ([] for i in range(4))
    
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
    

# Home pages for respective roles
def home(request):
    products = Product.objects.filter(pub_date__lte=datetime.now()).order_by('-pub_date')[0:4]
    return render(request, 'home.html', {"products": products})

@login_required(login_url='farm_coffee_app:login')
def admin_dashboard(request):
    products = Product.objects.filter(pub_date__lte=datetime.now()).order_by('-pub_date')
    employees = User.objects.filter(groups__name__in=['Employee'])
    context={'products': products, 'product_form': ProductForm}
    return render(request, 'admin/admin_dashboard.html', context)
    


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

@login_required(login_url='farm_coffee_app:login')
def view_history(request):
    orders = Order.objects.filter(user=request.user)
    context = {}
    if orders:
        items = [order for order in orders]
        items = Item.objects.filter(order__in=items)
        print("ITEMS", items)
        context = {'orders': orders, 'items': items}
        print(items)
        print(orders)
    return render(request, 'order/order_history_details.html', context)

def view_product_history(request, pk):
    items = Item.objects.filter(order=pk)
    quantity = Quantity.objects.filter(item__in=items)
    return render(request, 'order/order_history_details.html', {'items': zip(items, quantity)})



#Product CRUD
@login_required(login_url='farm_coffee_app:login')
@user_passes_test(is_manager, redirect_field_name="/") #check is the logged in user is manager else redirect to home page
def create_product(request):
    if request.method == "POST":
        data = request.POST
        data._mutable = True
        data["user"] = request.user
        data._mutable = False
        product_form = ProductForm(data)
        if product_form.is_valid():
            product_form.save()
            ProductForm()
            messages.success(request, ("Product added successfully!"))
            product_form = ProductForm()
        else:
            messages.error(request, (f'Product invalid'))
    else:
        product_form = ProductForm(instance=request.user)
    context = {'product_form':product_form}
    return render(request, 'product/product_form.html', context)

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

def filtered_menu(request, slug):
    print(slug)
    products = Product.objects.filter(category=slug)
    context = {'view_product_list': products}

    return render(request, 'menu.html', context)
        
class read_product_detail(generic.DetailView):
    model = Product
    template_name = 'product/read_product_detail.html'
    
    def get_queryset(self):
        return Product.objects.filter(pub_date__lte=datetime.now()).order_by('-pub_date')


#@user_passes_test(is_manager, redirect_field_name="/") #check is the logged in user is manager else redirect to home page
class update_product(LoginRequiredMixin, generic.UpdateView):
    model = Product
    fields = ['name', 'price', 'image', 'availability']
    template_name= 'product/update_product.html'
    success_url = '/admin_dashboard'
    def get_object(self, queryset=None):
        id = self.kwargs.get('pk')
        return get_object_or_404(Product, product_id=id)


# @user_passes_test(is_manager, redirect_field_name="/") #check is the logged in user is manager else redirect to home page
class delete_product(LoginRequiredMixin, generic.DeleteView):
    model = Product
    template_name = 'product/confirm_delete_product.html'
    success_url = '/admin_dashboard'


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
def total_cart_items(request):
    total_items = 0
    try:
        customer = Profile.objects.get(user=request.user)
        user = Cart.objects.filter(user=customer).values('id')[0]
        user = Cart.objects.get(id=user['id'])
        total_items = user.get_total
    except:
        print('----------------------> No Item is added to the cart')
    return total_items

def total_price(request):
    total_price = 0
    try:
        customer = Profile.objects.get(user=request.user)
        user = Cart.objects.filter(user=customer).values('id')[0]
        user = Cart.objects.get(id=user['id'])
        print("Two")
        total_price = user.get_total_price
        #it maybe html problem coz by defualt it reutrn 0 check line 747
    except:
        print('-------------------------> No Item was added to your cart')

    return total_price

@login_required(login_url='farm_coffee_app:login')
def cart(request):
 
    user = Profile.objects.get(user=request.user)
    products = Cart.objects.filter(user=user) 
    context = {
        'products': products, #this works
        'total_price': total_price(request), #  this works
        'cartProducts': total_cart_items(request)
        }
    return render(request,'cart/cart.html', context)
  
# Functions dealing with cart and checkout logic
@login_required(login_url='farm_coffee_app:login')
def checkout(request):
    user = Profile.objects.get(user=request.user)
    context = {'cartProducts':total_cart_items(request), 'total_price': total_price(request)}
    if request.method == "POST":
        data = request.POST
        data._mutable = True

        
        data["user"] = request.user
        data._mutable = False
        form = OrderForm(data)
        if form.is_valid():
            order = form.save()
            cart = Cart.objects.filter(user = user)
            for cart in cart:
                item = Item.objects.create(order=order, product=cart.product)
                Quantity.objects.create(item=item, quantity=cart.quantity)
            Cart.objects.filter(user=user).delete()
            messages.success(request, ("Your order has been submitted!"))
            return redirect('farm_coffee_app:home')
        error = form.errors
        for e in error:
            error = e
            messages.warning(request, error + ' is not valid')
        return redirect('farm_coffee_app:checkout')
    return render(request, 'checkout/checkout.html', context)

@login_required(login_url='farm_coffee_app:login')
def manage_cart(request):
    data = json.loads(request.body)
    product_id = data['product_id']
    action = data['action']
    print('Action ---->', action)
    print('Product ID ---->', product_id )
    if action == 'add':
        add_to_cart(request, product_id)
    else:
        remove_from_cart(request, product_id)
    return JsonResponse('Action Made', safe=False)

@login_required(login_url='farm_coffee_app:login')
def add_to_cart(request, product_id):
    user = Profile.objects.get(user=request.user)
    product = Product.objects.get(product_id=product_id)
    cart = Cart.objects.filter(user=user)
    messages.success(request, ("Product added to cart!"))
    if cart:
        item_present = Cart.objects.filter(user=user, product=product)
        if item_present:
            item_present.update(quantity=F('quantity') + 1)
        else:
            Cart.objects.create(user=user, product=product, quantity=1).save()
    else:
        Cart.objects.create(user=user, product=product, quantity=1)

@login_required(login_url='farm_coffee_app:login')
def remove_from_cart(request, product_id):

    user = Profile.objects.get(user=request.user)
    product = Product.objects.get(product_id=product_id)
    item_present = Cart.objects.filter(user=user, product=product)
    item_present.update(quantity=F('quantity') - 1 )
    item = item_present.values('quantity')[0]['quantity']
    if item <= 0:
        item_present.delete()



# Recommendation page
def recommendation_page(request):
    recommendations=recommendation_engine(request)
    
    return render(request, "recommendations/recommendation.html", {'recommended':recommendations})


# Creating Employees (For EMPLOYEES AND MANAGERS ONLY)
@login_required(login_url='farm_coffee_app:login')
@user_passes_test(is_manager, redirect_field_name="/") #check is the logged in user is manager else redirect to home page
def create_employee(request):
    user = Profile.objects.all()
    form = EmployeeForm()
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Employee: {form.cleaned_data["first_name"]} created')
            return redirect('farm_coffee_app:dashboard')
        error = form.error_messages
        for e in error:
            error = e
        messages.warning(request, error)
        return redirect('farm_coffee_app:create_employee')
    context = {'form':form, 'employee':user}
    return render(request, 'admin/admin_employee_creation.html', context)

@login_required(login_url='farm_coffee_app:login')
@user_passes_test(is_manager, redirect_field_name="/")
def employee_list(request):
    employees = User.objects.filter(groups__name__in=['Employee'])
    context = {'employees': employees}
    return render(request, 'admin/employee_list.html', context)

@login_required(login_url='farm_coffee_app:login')
@user_passes_test(is_manager, redirect_field_name="/")
def employee_details(request, pk):
    print("Hello World",pk)
    employee = User.objects.get(id=pk)
    context = {'employee': employee}
    return render(request, 'admin/employee_details.html', context)

@login_required(login_url='farm_coffee_app:login')
@user_passes_test(is_manager, redirect_field_name="/")
def employee_delete(request, pk):
    employee = User.objects.get(id=pk)
    if request.method == "POST":
        employee.delete()
        return redirect('farm_coffee_app:employee_list')
    context = {'employee':employee}
    return render(request, 'admin/delete_employee.html', context)


# Order Management (For EMPLOYEES AND MANAGERS ONLY)
@login_required(login_url='farm_coffee_app:login')
@user_passes_test(is_employee, redirect_field_name="/")
def order_list(request):
    orders = Order.objects.all()

    orderStatus ={
        "ORD":'Ordering',
        "PRE":'Preparing',
        "DEL":'Delivering',
        "DEE":'Delivered',
    }

    context = {
        'orders': orders,
        "orderStatus" : orderStatus
        }
    return render(request, 'admin/order_list.html', context)


@login_required(login_url='farm_coffee_app:login')
@user_passes_test(is_employee, redirect_field_name="/")
def update_order(request, pk):
        order = Order.objects.get(order_id=pk)
        form = OrderForm(instance=order)
        if request.method == 'POST':
            form = OrderForm(request.POST, instance=order)
            if form.is_valid():
                form.save()
                messages.success(request, 'Order is updated successfully')
                return redirect(reverse('farm_coffee_app:update_order', args=[pk]))
            error = form.errors
            for e in error:
                error = e
            messages.warning(request, f'Invalid {error}')
            return redirect(reverse('farm_coffee_app:update_order', args=[pk]))
        context = {'form': form}
        return render(request, 'admin/update_order.html', context)
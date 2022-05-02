from unicodedata import name
from django.urls import path
from .import views

app_name = 'farm_coffee_app'

urlpatterns = [
    path('', views.home, name="home"),
    path('menu', views.menu),
    path("register", views.register_request, name='register'),
    path("login", views.login_request, name="login"),
    path('logout', views.logout_request, name='logout'),
    path("profile", views.profilepage, name = 'profilepage'),
    # path('<int:user_id>/', views.user_details, name='detail'),
    path("password_reset", views.password_reset_request, name="password_reset"),

    # urls for adding-to-cart
    
    # urls for product
    path('create_product', views.create_product.as_view(), name='create_product'),
    path('list/', views.read_product_list.as_view(), name='read_product_list'),
    path('details/<int:pk>/', views.read_product_detail.as_view(), name='read_product_detail'),
    path('update/<int:pk>/', views.update_product.as_view(), name='update_product'),
    path('delete/<int:pk>/', views.delete_product.as_view(), name='delete_product'),

    # urls for order
    # path('create_order', views.create_order.as_view(), name='total_order_form')

    # urls for review
    path('review/', views.create_review, name='create_review'),
    path('read_review/', views.read_review.as_view(), name='read_product_detail'),
    path('update_review/<int:pk>/', views.update_review.as_view(), name='update_review'),
    path('delete_review/<int:pk>/', views.delete_review.as_view(), name='delete_review'),

    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),


]
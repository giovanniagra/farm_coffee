from unicodedata import name
from django.urls import path
from .import views
from django.views.decorators.csrf import csrf_exempt

app_name = 'farm_coffee_app'

urlpatterns = [
    path('', views.home, name="home"),
    path('menu', views.menu.as_view(), name='menu'),
    # path("register", views.registrationview, name='register'),
    # path("login", views.loginView, name="login"),
    # path('logout', views.logoutuser, name='logout'),
    path("profile", views.profilepage, name = 'profilepage'),
    # # path('<int:user_id>/', views.user_details, name='detail'),
    # path("password_reset", views.password_reset_request, name="password_reset"),

    # urls for customer
    path('ordered_history/', views.view_history, name="history"),
	path('ordered_products/<pk>/', views.view_product_history, name="ordered_products"),
    
    # urls for product
    path('create_product', views.create_product.as_view(), name='create_product'),
    path('list/', views.read_product_list.as_view(), name='read_product_list'),
    path('details/<int:pk>/', views.read_product_detail.as_view(), name='read_product_detail'),
    path('update/<int:pk>/', views.update_product.as_view(), name='update_product'),
    path('delete/<int:pk>/', views.delete_product.as_view(), name='delete_product'),

    # urls for recommendation
    path('recommendations/', views.recommendation_page, name='recommendations'),

    # urls for review
    path('review/', views.create_review, name='create_review'),
    path('read_review/', views.read_review.as_view(), name='read_product_detail'),
    path('update_review/<int:pk>/', views.update_review.as_view(), name='update_review'),
    path('delete_review/<int:pk>/', views.delete_review.as_view(), name='delete_review'),

    #urls for cart
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_item/', views.update_item, name='update_item'),
    path('processOrder/', views.processOrder, name='placeorder'),

]
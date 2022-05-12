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
    path('create_product', views.create_product, name='create_product'),
    path('list/', views.read_product_list.as_view(), name='read_product_list'),
    path('details/<int:pk>/', views.read_product_detail.as_view(), name='read_product_detail'),
    path('delete/<pk>/', views.delete_product.as_view(), name='delete_product'),
    path('update/<pk>/', views.update_product.as_view(), name='update_product'),

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
    path('manage_cart/', views.manage_cart, name="manage_cart"),
    # path('update_item/', views.update_item, name='update_item'),
    # path('processOrder/', views.processOrder, name='placeorder'),

    # urls for workers
    path('admin_dashboard/', views.admin_dashboard, name='dashboard'),
    path('create_employee/', views.create_employee, name="create_employee"),
    path('employee_list/', views.employee_list, name='employee_list'),
    path('employee_details/<pk>', views.employee_details, name="employee_details"),
    path('delete_employee/<pk>', views.employee_delete, name="delete_employee"),
    path('order_list/', views.order_list, name="order_list"),
    # path('order_details/', views.ord)
    path('update_order/<pk>', views.update_order, name="update_order")
]
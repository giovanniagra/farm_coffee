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
    path('create_product', views.create_product.as_view(), name='create_product'),
    path('list', views.read_product_list.as_view(), name='read_product_list'),
    path('details/<int:pk>/', views.read_product_detail.as_view(), name='read_product_detail'),
]
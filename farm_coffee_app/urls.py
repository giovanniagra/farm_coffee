from django.urls import path
from .import views

urlpatterns = [
    path('', views.home, name="home"),
    path('menu', views.menu),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
]
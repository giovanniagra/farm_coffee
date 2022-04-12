from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html', {})

def menu(request):
    return render(request, 'menu.html', {})

def signup(request):
    return render(request, "signup.html", {})

def signout(request):
    return render(request, "signout.html", {})

def signup(request):
    pass
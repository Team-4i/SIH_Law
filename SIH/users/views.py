from django.shortcuts import render, redirect
from django.contrib.auth import logout
# Create your views here.

def home(request):
    user = request.user
    return render(request, "home.html", {'user': user})


def logout_view(request):
    logout(request)
    return redirect('/')

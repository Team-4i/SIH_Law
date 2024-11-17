from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('logout/', views.logout_view), 
    path('chat/', views.chat),
    
]

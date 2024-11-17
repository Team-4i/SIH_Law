from django.urls import path
from . import views

app_name = 'snake_ladder'

urlpatterns = [
    path('board/', views.game_board, name='game_board'),
]

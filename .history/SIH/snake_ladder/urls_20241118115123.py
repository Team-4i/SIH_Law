from django.urls import path
from . import views

app_name = 'snake_ladder'

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_room, name='create_room'),
    path('join/<uuid:room_id>/', views.join_room, name='join_room'),
    path('board/<uuid:room_id>/', views.game_board, name='game_board'),
    path('game-state/<uuid:room_id>/', views.game_state, name='game_state'),
    path('room/<uuid:room_id>/', views.room_detail, name='room_detail'),
]
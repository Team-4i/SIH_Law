from django.urls import path
from . import views

app_name = 'snake_ladder'

urlpatterns = [
    path('create-room/', views.create_room, name='create_room'),
    path('room/<uuid:room_id>/', views.room_detail, name='room_detail'),
    path('join/<uuid:room_id>/', views.join_room, name='join_room'),
    path('board/<uuid:room_id>/', views.game_board, name='game_board'),
    path('game-state/<uuid:room_id>/', views.get_game_state, name='game_state'),
]

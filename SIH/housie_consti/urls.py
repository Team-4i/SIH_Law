from django.urls import path
from . import views

app_name = 'housie_consti'

urlpatterns = [
    path('create/', views.create_room, name='create_room'),
    path('join/<uuid:room_id>/', views.join_room, name='join_room'),
    path('room/<uuid:room_id>/', views.room_detail, name='room_detail'),
    path('game/<uuid:room_id>/', views.game_board, name='game_board'),
]

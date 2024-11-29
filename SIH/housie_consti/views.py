from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import GameRoom

@login_required
def create_room(request):
    if request.method == 'POST':
        room = GameRoom.objects.create(creator=request.user)
        room.players.add(request.user)
        return redirect('housie_consti:room_detail', room_id=room.room_id)
    return render(request, 'housie_consti/create_room.html')

@login_required
def room_detail(request, room_id):
    room = get_object_or_404(GameRoom, room_id=room_id)
    player_count = room.players.count()
    
    if player_count >= 4 and not room.game_started:
        room.game_started = True
        room.save()
        return redirect('housie_consti:game_board', room_id=room_id)
        
    context = {
        'room': room,
        'player_count': player_count,
        'players_needed': 4 - player_count
    }
    return render(request, 'housie_consti/room_detail.html', context)

@login_required
def join_room(request, room_id):
    room = get_object_or_404(GameRoom, room_id=room_id)
    if request.user not in room.players.all() and room.players.count() < 4:
        room.players.add(request.user)
    return redirect('housie_consti:room_detail', room_id=room_id)

@login_required
def game_board(request, room_id):
    room = get_object_or_404(GameRoom, room_id=room_id)
    if not room.game_started or request.user not in room.players.all():
        return redirect('housie_consti:room_detail', room_id=room_id)
    return render(request, 'housie_consti/game_board.html', {'room': room})

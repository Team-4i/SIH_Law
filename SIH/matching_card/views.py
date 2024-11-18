from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import GameRoom
import qrcode
from io import BytesIO
from base64 import b64encode
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@login_required
def create_room(request):
    if request.method == 'POST':
        room = GameRoom.objects.create(creator=request.user)
        room.players.add(request.user)
        return redirect('matching_card:room_detail', room_id=room.room_id)
    return render(request, 'matching_card/create_room.html')

@login_required
def game_board(request, room_id):
    room = get_object_or_404(GameRoom, room_id=room_id)
    if request.user not in room.players.all():
        return redirect('matching_card:join_room', room_id=room_id)
    
    context = {
        'room': room,
        'players': room.players.all(),
    }
    return render(request, 'matching_card/game_board.html', context)


@login_required
def room_detail(request, room_id):
    room = get_object_or_404(GameRoom, room_id=room_id)
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    room_url = request.build_absolute_uri(reverse('matching_card:join_room', args=[room_id]))
    qr.add_data(room_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_code = b64encode(buffer.getvalue()).decode()
    
    context = {
        'room': room,
        'qr_code': qr_code,
        'room_url': room_url
    }
    return render(request, 'matching_card/room_detail.html', context)

@login_required
def join_room(request, room_id):
    room = get_object_or_404(GameRoom, room_id=room_id)
    if request.user not in room.players.all():
        if room.players.count() < 2:
            room.players.add(request.user)
            
            # Notify WebSocket about new player
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'card_room_{room_id}',
                {
                    'type': 'room_event',
                    'event_type': 'player_update',
                    'data': {
                        'players': list(room.players.values('id', 'username')),
                        'player_count': room.players.count()
                    }
                }
            )
    return redirect('matching_card:room_detail', room_id=room_id)
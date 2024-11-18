from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Cell, GameRoom, PlayerPosition
import qrcode
import qrcode.image.svg
from io import BytesIO
from base64 import b64encode
import time
from django.http import JsonResponse

def generate_dice_roll():
    """
    Generates a pseudo-random dice roll using timestamp microseconds.
    Returns a tuple of (dice_roll, timestamp) for verification.
    """
    timestamp = int(time.time() * 1000000)
    dice_roll = ((timestamp % 6) + 1)  # 1 to 6
    return dice_roll, timestamp

@login_required
def game_board(request, room_id):
    room = get_object_or_404(GameRoom, room_id=room_id)
    if request.user not in room.players.all():
        return redirect('snake_ladder:join_room', room_id=room_id)
    
    # Get cells first
    cells = Cell.objects.all().order_by('number')
    
    # Set initial turn if not set
    if not room.current_turn:
        room.current_turn = room.creator
        room.save()
    
    # Get or create player positions
    positions = {}
    for player in room.players.all():
        position, _ = PlayerPosition.objects.get_or_create(
            room=room, 
            player=player,
            defaults={'position': 1}
        )
        positions[player.id] = position.position
    
    if request.method == 'POST' and request.POST.get('roll'):
        if room.current_turn == request.user:
            dice_roll, timestamp = generate_dice_roll()
            player_position = PlayerPosition.objects.get(room=room, player=request.user)
            new_position = player_position.position + dice_roll
            
            # Update position logic
            if 94 <= player_position.position <= 99:
                if new_position > 100:
                    new_position = player_position.position
                elif new_position == 100:
                    new_position = 1
            elif new_position > 100:
                new_position = 1
            
            # Check for snakes and ladders
            current_cell = cells.filter(number=new_position).first()
            if current_cell and current_cell.destination:
                new_position = current_cell.destination
            
            # Update player position
            player_position.position = new_position
            player_position.save()
            
            # Update turn
            player_list = list(room.players.all())
            current_index = player_list.index(request.user)
            next_index = (current_index + 1) % len(player_list)
            room.current_turn = player_list[next_index]
            room.save()
            
            return redirect('snake_ladder:game_board', room_id=room_id)
    
    board = []
    numbers = list(range(100, 0, -1))
    
    for i in range(10):
        row = numbers[i * 10:(i + 1) * 10]
        if i % 2 != 0:
            row = reversed(row)
        board.append(row)
    
    visible_cells = {}
    if request.user.id in positions:
        current_position = positions[request.user.id]
        cell = cells.filter(number=current_position).first()
        if cell:
            visible_cells[current_position] = {
                'content': cell.content,
                'timestamp': time.time()
            }
    
    context = {
        'board': board,
        'cells': {cell.number: cell for cell in cells},
        'current_position': positions[request.user.id],
        'positions': positions,
        'room': room,
        'players': room.players.all(),
        'current_turn': room.current_turn,
        'visible_cells': visible_cells,
    }
    return render(request, 'game_board.html', context)

@login_required
def create_room(request):
    if request.method == 'POST':
        room = GameRoom.objects.create(creator=request.user)
        room.players.add(request.user)
        return redirect('snake_ladder:room_detail', room_id=room.room_id)
    return render(request, 'create_room.html')

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
    room_url = request.build_absolute_uri(reverse('snake_ladder:join_room', args=[room_id]))
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
    return render(request, 'room_detail.html', context)

@login_required
def join_room(request, room_id):
    room = get_object_or_404(GameRoom, room_id=room_id)
    if request.user not in room.players.all():
        room.players.add(request.user)
    return redirect('snake_ladder:game_board', room_id=room_id)

@login_required
def get_game_state(request, room_id):
    room = get_object_or_404(GameRoom, room_id=room_id)
    positions = {}
    for player in room.players.all():
        position = PlayerPosition.objects.get(room=room, player=player)
        positions[player.id] = position.position
    
    return JsonResponse({
        'positions': positions,
        'current_turn': room.current_turn.id,
        'current_turn_username': room.current_turn.username,
        'players': [{
            'id': player.id,
            'username': player.username,
            'position': positions[player.id]
        } for player in room.players.all()]
    })

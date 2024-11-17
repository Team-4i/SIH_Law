from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Cell, GameRoom
import qrcode
import qrcode.image.svg
from io import BytesIO
from base64 import b64encode
import time

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
    
    # Set initial turn if not set
    if not room.current_turn:
        room.current_turn = room.creator
        room.save()
    
    cells = Cell.objects.all().order_by('number')
    
    # Get all player positions
    positions = {}
    for player in room.players.all():
        positions[player.id] = request.session.get(f'position_{room_id}_{player.id}', 1)
    
    last_roll = request.session.get(f'last_roll_{room_id}_{request.user.id}')
    
    if request.method == 'POST' and request.POST.get('roll'):
        if room.current_turn == request.user:
            dice_roll, timestamp = generate_dice_roll()
            new_position = positions[request.user.id] + dice_roll
            
            # Special handling for positions 94-99
            if 94 <= positions[request.user.id] <= 99:
                if new_position > 100:
                    new_position = positions[request.user.id]
                elif new_position == 100:
                    request.session[f'position_{room_id}_{request.user.id}'] = 1
                    request.session[f'last_roll_{room_id}_{request.user.id}'] = None
            elif new_position > 100:
                new_position = 1
                request.session[f'position_{room_id}_{request.user.id}'] = new_position
                request.session[f'last_roll_{room_id}_{request.user.id}'] = None
            
            # Normal game progression
            current_cell = cells.filter(number=new_position).first()
            if current_cell and current_cell.destination:
                new_position = current_cell.destination
            
            # Store position in session
            request.session[f'position_{room_id}_{request.user.id}'] = new_position
            request.session[f'last_roll_{room_id}_{request.user.id}'] = dice_roll
            request.session.modified = True
            
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
    
    context = {
        'board': board,
        'cells': {cell.number: cell for cell in cells},
        'current_position': positions[request.user.id],
        'positions': positions,
        'last_roll': last_roll,
        'room': room,
        'players': room.players.all(),
        'current_turn': room.current_turn,
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

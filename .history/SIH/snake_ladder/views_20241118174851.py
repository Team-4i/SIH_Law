from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Cell, GameRoom, PlayerPosition, CellHistory
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
    
    # Create cells dictionary for template lookup
    cells_dict = {cell.number: cell for cell in cells}
    
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
            
            # Store the new position in session for content visibility
            request.session[f'last_move_{room_id}'] = {
                'position': new_position,
                'timestamp': time.time()
            }
            
            # Update position logic
            if 94 <= player_position.position <= 99:
                if new_position > 100:
                    new_position = player_position.position
                elif new_position == 100:
                    new_position = 1
            elif new_position > 100:
                new_position = 1
            
            # Get current cell for history
            current_cell = cells.filter(number=new_position).first()
            
            # Update player position
            player_position.position = new_position
            player_position.save()
            
            # Add cell history
            if current_cell:
                CellHistory.objects.create(
                    player=request.user,
                    room=room,
                    cell=current_cell
                )
            
            # Update turn
            player_list = list(room.players.all())
            current_index = player_list.index(request.user)
            next_index = (current_index + 1) % len(player_list)
            room.current_turn = player_list[next_index]
            room.save()
            
            cells_dict = {}
            for cell in cells:
                cells_dict[cell.number] = cell
            
            context = {
                'room': room,
                'board': board,
                'cells': cells_dict,  # Pass the dictionary instead of queryset
                'players': room.players.all(),
                'current_turn': room.current_turn,
                'positions': positions,
                'visible_cells': visible_cells,
            }
            return render(request, 'game_board.html', context)
    
    # Modified board generation
    board = []
    numbers = list(range(100, 0, -1))  # 100 to 1
    
    for i in range(10):
        row = numbers[i * 10:(i + 1) * 10]
        if i % 2 == 0:  # Changed condition to make it consistent
            row = list(reversed(row))  # Explicitly convert to list
        board.append(list(row))  # Ensure each row is a list
    
    # Create a dictionary of cells for easy lookup
    cells_dict = {cell.number: cell for cell in cells}
    
    visible_cells = {}
    if request.user.id in positions:
        current_position = positions[request.user.id]
        cell = cells.filter(number=current_position).first()
        if cell:
            # Only show content for 30 seconds after landing
            current_time = time.time()
            visible_cells[current_position] = {
                'content': cell.content,
                'timestamp': current_time,
                'expires': current_time + 30  # 30 seconds visibility
            }
    
    context = {
        'board': board,
        'cells': cells_dict,
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
def game_state(request, room_id):
    try:
        room = get_object_or_404(GameRoom, room_id=room_id)
        room.refresh_from_db()
        
        positions = {}
        visible_cells = {}
        player_colors = room.get_player_color()
        
        # Get fresh position data
        for player in room.players.all():
            position = PlayerPosition.objects.get(room=room, player=player).position
            positions[player.id] = position
            
            # Only show content for the current user's position
            if player.id == request.user.id:
                cell = Cell.objects.filter(number=position).first()
                if cell:
                    # Get the last shown positions from session
                    shown_positions = request.session.get(f'shown_positions_{room_id}', [])
                    
                    # Only include cell content if position hasn't been shown before
                    if position not in shown_positions:
                        visible_cells[position] = {
                            'content': cell.content,
                            'timestamp': time.time(),
                            'expires': time.time() + 30
                        }
                        # Update shown positions in session
                        shown_positions.append(position)
                        request.session[f'shown_positions_{room_id}'] = shown_positions
                        request.session.modified = True
        
        response_data = {
            'positions': positions,
            'current_turn': room.current_turn.id,
            'current_turn_username': room.current_turn.username,
            'visible_cells': visible_cells,
            'players': [{
                'id': player.id,
                'username': player.username,
                'position': positions[player.id],
                'color': player_colors[player][0]
            } for player in room.players.all()]
        }
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def home(request):
    return render(request, 'home.html')

def verify_board(request):
    cells = Cell.objects.all().order_by('number')
    snake_ladder_cells = cells.filter(cell_type='SNAKE_LADDER').values_list('number', flat=True)
    return JsonResponse({
        'total_cells': cells.count(),
        'snake_ladder_cells': list(snake_ladder_cells),
        'percentage': (len(snake_ladder_cells) / cells.count()) * 100
    })

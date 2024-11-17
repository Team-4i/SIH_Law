from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Cell
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
def game_board(request):
    cells = Cell.objects.all().order_by('number')
    current_position = request.session.get('position', 1)
    last_roll = request.session.get('last_roll')
    
    if request.method == 'POST' and request.POST.get('roll'):
        dice_roll, timestamp = generate_dice_roll()
        new_position = current_position + dice_roll
        
        # Special handling for positions 94-99
        if 94 <= current_position <= 99:
            if new_position > 100:
                # Stay at current position if roll is too high
                new_position = current_position
            elif new_position == 100:
                # Win condition
                request.session['position'] = 1
                request.session['last_roll'] = None
                return redirect(reverse('snake_ladder:game_board'))
        elif new_position > 100:
            # Reset game for positions < 94
            new_position = 1
            request.session['position'] = new_position
            request.session['last_roll'] = None
            return redirect(reverse('snake_ladder:game_board'))
        
        # Normal game progression
        current_cell = cells.filter(number=new_position).first()
        if current_cell and current_cell.destination:
            new_position = current_cell.destination
        
        request.session['position'] = new_position
        request.session['last_roll'] = dice_roll
        return redirect(reverse('snake_ladder:game_board'))
    
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
        'current_position': current_position,
        'last_roll': last_roll,
    }
    return render(request, 'game_board.html', context)

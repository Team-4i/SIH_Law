from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Cell
import time

@login_required
def game_board(request):
    cells = Cell.objects.all().order_by('number')
    
    # Create a dynamic seed based on timestamp microseconds
    current_position = request.session.get('position', 1)
    
    # Generate dice roll using timestamp
    if request.GET.get('roll'):
        timestamp = int(time.time() * 1000000)
        dice_roll = ((timestamp % 6) + 1)  # 1 to 6
        new_position = min(current_position + dice_roll, 100)
        request.session['position'] = new_position
        current_position = new_position
    
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
    }
    return render(request, 'game_board.html', context)

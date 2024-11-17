from django.shortcuts import render
from .models import Cell

def game_board(request):
    cells = Cell.objects.all().order_by('number')
    
    # Create a 10x10 board matrix (from 100 to 1)
    board = []
    numbers = list(range(100, 0, -1))
    
    for i in range(10):
        row = numbers[i * 10:(i + 1) * 10]
        # Reverse alternate rows for snake pattern
        if i % 2 != 0:
            row = reversed(row)
        board.append(row)
    
    context = {
        'board': board,
        'cells': {cell.number: cell for cell in cells}
    }
    return render(request, 'templates/game_board.html', context)

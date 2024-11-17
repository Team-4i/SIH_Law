from django.db import models
from django.contrib.auth.models import User
import uuid

class Cell(models.Model):
    number = models.IntegerField(unique=True)
    content = models.TextField(help_text="Educational content for this cell")
    cell_type = models.CharField(
        max_length=10,
        choices=[
            ('NORMAL', 'Normal Cell'),
            ('SNAKE', 'Snake Head'),
            ('LADDER', 'Ladder Bottom'),
        ],
        default='NORMAL'
    )
    destination = models.IntegerField(null=True, blank=True, 
        help_text="Destination cell number for snakes and ladders")
    
    def __str__(self):
        return f"Cell {self.number}"

    class Meta:
        ordering = ['number']

class GameRoom(models.Model):
    room_id = models.UUIDField(default=uuid.uuid4, unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    players = models.ManyToManyField(User, related_name='joined_rooms')
    current_turn = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='current_turn_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    PLAYER_COLORS = {
        0: ('blue-500', 'Blue'),
        1: ('red-500', 'Red'),
        2: ('green-500', 'Green'),
        3: ('purple-500', 'Purple'),
    }
    
    def get_player_color(self):
        player_dict = {}
        player_list = list(self.players.all())
        for player in player_list:
            try:
                index = player_list.index(player)
                player_dict[player] = self.PLAYER_COLORS[index]
            except (ValueError, KeyError):
                player_dict[player] = ('gray-500', 'Gray')
        return player_dict
    
    def __str__(self):
        return f"Room by {self.creator.username}"

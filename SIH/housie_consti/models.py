from django.db import models
from django.contrib.auth.models import User
import uuid

class GameRoom(models.Model):
    room_id = models.UUIDField(default=uuid.uuid4, unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_housie_rooms')
    players = models.ManyToManyField(User, related_name='joined_housie_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    game_started = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Housie Room by {self.creator.username}"
from django.db import models
from django.contrib.auth.models import User
import uuid

class GameRoom(models.Model):
    room_id = models.UUIDField(default=uuid.uuid4, unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_card_rooms')
    players = models.ManyToManyField(User, related_name='joined_card_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Card Room by {self.creator.username}"
    
class Article(models.Model):
    number = models.IntegerField(unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    def __str__(self):
        return f"Article {self.number}: {self.title}"

class PlayerHand(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    game_room = models.ForeignKey(GameRoom, on_delete=models.CASCADE)
    articles = models.ManyToManyField(Article)
    score = models.IntegerField(default=0)
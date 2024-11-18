from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import GameRoom, Article, PlayerHand
import random

class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'card_room_{self.room_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get('type')
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'room_event',
                'event_type': event_type,
                'data': data
            }
        )

    async def room_event(self, event):
        # Send event to WebSocket
        await self.send(text_data=json.dumps(event))
        

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'game_{self.room_id}'
        self.user = self.scope['user']
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'start_game':
            await self.start_game()
        elif action == 'draw_card':
            await self.draw_card(data)
        elif action == 'discard_card':
            await self.discard_card(data)
        elif action == 'keep_card':
            await self.keep_card(data)

    async def start_game(self):
        await self.initialize_game()
        game_state = await self.get_game_state()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_message',
                'message': {
                    'action': 'game_started',
                    'state': game_state
                }
            }
        )

    @database_sync_to_async
    def initialize_game(self):
        room = GameRoom.objects.get(room_id=self.room_id)
        articles = list(Article.objects.all())
        
        # Clear existing hands
        PlayerHand.objects.filter(game_room=room).delete()
        
        # Create new hands for each player
        for player in room.players.all():
            player_articles = random.sample(articles, 7)
            hand = PlayerHand.objects.create(
                player=player,
                game_room=room
            )
            hand.articles.set(player_articles)

    @database_sync_to_async
    def get_game_state(self):
        room = GameRoom.objects.get(room_id=self.room_id)
        players_data = []
        
        # Get creator (Player 1) first
        creator = room.creator
        creator_hand = PlayerHand.objects.get(player=creator, game_room=room)
        players_data.append({
            'id': creator.id,
            'username': creator.username,
            'cards': [
                {'number': article.number, 'title': article.title}
                for article in creator_hand.articles.all()
            ],
            'score': creator_hand.score,
            'isCreator': True
        })
        
        # Get other player (Player 2)
        other_player = room.players.exclude(id=creator.id).first()
        if other_player:
            other_hand = PlayerHand.objects.get(player=other_player, game_room=room)
            players_data.append({
                'id': other_player.id,
                'username': other_player.username,
                'cards': [
                    {'number': article.number, 'title': article.title}
                    for article in other_hand.articles.all()
                ],
                'score': other_hand.score,
                'isCreator': False
            })
        
        return {
            'players': players_data,
            'current_player': players_data[0]['id'] if players_data else None
        }

    async def draw_card(self, data):
        article = await self.get_random_article()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_message',
                'message': {
                    'action': 'card_drawn',
                    'card': {
                        'number': article.number,
                        'description': article.description
                    }
                }
            }
        )

    @database_sync_to_async
    def get_random_article(self):
        return random.choice(list(Article.objects.all()))

    async def game_message(self, event):
        await self.send(text_data=json.dumps(event['message']))
        
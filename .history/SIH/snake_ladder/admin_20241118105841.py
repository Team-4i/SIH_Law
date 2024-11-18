from django.contrib import admin
from .models import Cell, GameRoom, PlayerPosition

@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ('number', 'cell_type', 'destination')
    list_filter = ('cell_type',)
    search_fields = ('number', 'content')
    ordering = ('number',)

@admin.register(GameRoom)
class GameRoomAdmin(admin.ModelAdmin):
    list_display = ('creator', 'room_id', 'current_turn', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('creator__username', 'room_id')
    date_hierarchy = 'created_at'

@admin.register(PlayerPosition)
class PlayerPositionAdmin(admin.ModelAdmin):
    list_display = ('player', 'room', 'position')
    list_filter = ('room',)
    search_fields = ('player__username',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('cell_number', 'question_text')
    search_fields = ('question_text', 'answer')
    ordering = ('cell_number',)

@admin.register(PlayerProgress)
class PlayerProgressAdmin(admin.ModelAdmin):
    list_display = ('player', 'game_room', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('player__username',)
    date_hierarchy = 'created_at'
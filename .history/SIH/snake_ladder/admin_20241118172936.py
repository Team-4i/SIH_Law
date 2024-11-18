from django.contrib import admin
from .models import Cell, GameRoom, PlayerPosition, CellHistory


@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ('number', 'cell_type')
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

@admin.register(CellHistory)
class CellHistoryAdmin(admin.ModelAdmin):
    list_display = ('player', 'room', 'cell', 'visited_at')
    list_filter = ('room', 'player', 'visited_at')
    search_fields = ('player__username', 'cell__number')
    date_hierarchy = 'visited_at'

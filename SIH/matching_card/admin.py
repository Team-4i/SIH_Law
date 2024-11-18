from django.contrib import admin
from .models import GameRoom, Article, PlayerHand

# Register your models here.

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('number', 'title')
    search_fields = ('number', 'title', 'description')

admin.site.register(GameRoom)
admin.site.register(PlayerHand)
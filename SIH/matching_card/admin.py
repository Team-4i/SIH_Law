from django.contrib import admin
from .models import GameRoom, Article, PlayerHand

# Register your models here.

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('article_number', 'case_name', 'year')
    search_fields = ('article_number', 'case_name', 'description')

admin.site.register(GameRoom)
admin.site.register(PlayerHand)
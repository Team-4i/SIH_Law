from django.db import models
from django.contrib.auth.models import User

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

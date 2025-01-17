# Generated by Django 5.1.3 on 2024-11-18 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snake_ladder', '0004_playerposition'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cell',
            name='destination',
        ),
        migrations.AlterField(
            model_name='cell',
            name='cell_type',
            field=models.CharField(choices=[('NORMAL', 'Normal Cell'), ('SNAKE_LADDER', 'Snake-Ladder Cell')], default='NORMAL', max_length=15),
        ),
    ]

# Generated by Django 3.2 on 2024-07-03 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='bio',
            field=models.TextField(default='Пусто'),
        ),
    ]

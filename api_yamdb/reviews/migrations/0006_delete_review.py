# Generated by Django 3.2.16 on 2024-07-06 15:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0005_alter_review_author'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Review',
        ),
    ]

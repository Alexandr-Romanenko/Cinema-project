# Generated by Django 4.2 on 2023-06-27 14:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cinema_app', '0002_purchase_quantity'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='moviesession',
            options={'ordering': ['is_active', 'session_show_start_date', 'movie_title']},
        ),
        migrations.AlterModelOptions(
            name='purchase',
            options={'ordering': ['-purchase_date']},
        ),
    ]

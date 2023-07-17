# Generated by Django 4.2 on 2023-07-07 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cinema_app', '0005_delete_tokenlifetimeexpired'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='moviesession',
            options={'ordering': ['session_show_start_date', 'movie_title']},
        ),
        migrations.RemoveField(
            model_name='moviesession',
            name='is_active',
        ),
        migrations.AddField(
            model_name='moviesession',
            name='image',
            field=models.ImageField(blank=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='moviesession',
            name='image_title',
            field=models.ImageField(blank=True, upload_to=''),
        ),
    ]

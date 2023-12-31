# Generated by Django 4.2 on 2023-06-27 15:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authtoken', '0003_tokenproxy'),
        ('cinema_app', '0003_alter_moviesession_options_alter_purchase_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='TokenLifetimeExpired',
            fields=[
                ('token_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='authtoken.token')),
                ('last_action', models.DateTimeField(null=True)),
            ],
            bases=('authtoken.token',),
        ),
    ]

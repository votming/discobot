# Generated by Django 4.1.2 on 2023-03-05 20:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_movie_dont_want_to_watch_alter_user_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('config', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('guild', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.guild')),
            ],
        ),
    ]
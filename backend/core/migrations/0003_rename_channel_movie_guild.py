# Generated by Django 4.1.2 on 2022-10-24 17:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_rename_channel_guild_alter_movie_already_seen_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='movie',
            old_name='channel',
            new_name='guild',
        ),
    ]

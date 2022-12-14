# Generated by Django 4.1.2 on 2022-10-25 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='session',
            name='unique_guild_seen_at_none',
        ),
        migrations.AddConstraint(
            model_name='session',
            constraint=models.UniqueConstraint(condition=models.Q(('seen_at', None)), fields=('guild',), name='unique_guild_seen_at_none'),
        ),
    ]

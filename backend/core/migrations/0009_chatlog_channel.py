# Generated by Django 4.1.2 on 2023-03-07 10:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_chatlog_fact'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatlog',
            name='channel',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='chat_logs', to='core.channel'),
            preserve_default=False,
        ),
    ]
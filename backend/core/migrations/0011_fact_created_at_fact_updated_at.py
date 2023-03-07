# Generated by Django 4.1.2 on 2023-03-07 11:48

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_fact_chat_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='fact',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fact',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]

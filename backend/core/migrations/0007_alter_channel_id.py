# Generated by Django 4.1.2 on 2023-03-05 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_channel_config'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='id',
            field=models.CharField(max_length=30, primary_key=True, serialize=False),
        ),
    ]
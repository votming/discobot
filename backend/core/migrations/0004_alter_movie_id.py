# Generated by Django 4.1.2 on 2022-10-24 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_rename_channel_movie_guild'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='id',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
    ]

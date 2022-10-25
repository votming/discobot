# Generated by Django 4.1.2 on 2022-10-25 10:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_movie_actors'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ranking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField()),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.movie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.user')),
            ],
        ),
        migrations.AddField(
            model_name='movie',
            name='ranking',
            field=models.ManyToManyField(related_name='+', through='core.Ranking', to='core.user'),
        ),
    ]

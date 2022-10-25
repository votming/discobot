from django.db import models
from django.db.models import Q


# Create your models here.
from django.db.models import UniqueConstraint


class Guild(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)


class User(models.Model):
    id = models.CharField(max_length=40, primary_key=True)
    name = models.CharField(max_length=50)
    avatar = models.CharField(max_length=400, null=True)
    mention = models.CharField(max_length=40, null=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)


class Movie(models.Model):
    uuid = models.CharField(max_length=50)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    actors = models.CharField(max_length=200, default='Нет информации')
    year = models.IntegerField(null=True)
    image = models.CharField(max_length=450, default=None, null=True)
    already_seen = models.ManyToManyField(User, blank=True, related_name='already_seen')
    want_to_see = models.ManyToManyField(User, blank=True, related_name='want_to_see')
    rankings = models.ManyToManyField(User, through='Ranking')
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        unique_together = ('uuid', 'guild')


class Session(models.Model):
    id = models.AutoField(primary_key=True)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, null=True, blank=True, on_delete=models.CASCADE)
    audience = models.ManyToManyField(User, default=[], related_name='+')
    seen_at = models.DateTimeField(null=True, default=None)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['guild'], condition=Q(seen_at=None),
                             name='unique_guild_seen_at_none')
        ]

    @property
    def available_movies(self):
        if self.audience.all():
            return Movie.objects.filter(guild=self.guild, session__seen_at=None).exclude(already_seen__in=self.audience.all()).all()
        return Movie.objects.filter(guild=self.guild, session__seen_at=None).all()

    @property
    def audience_want_to_see_movies(self):
        if self.audience.all():
            return Movie.objects.filter(guild=self.guild, session__seen_at=None, want_to_see__in=self.audience.all()).all()
        return []


class Ranking(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_rankings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_rankings')
    rating = models.IntegerField()

    class Meta:
        unique_together = [['movie', 'user']]

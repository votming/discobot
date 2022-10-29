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
    id = models.IntegerField(max_length=40, primary_key=True)
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

    @property
    def average_rating(self):
        rows = Ranking.objects.filter(movie=self)
        if len(rows) > 0:
            return sum([row.rating for row in rows])/len(rows)
        else:
            return None



class Session(models.Model):
    id = models.AutoField(primary_key=True)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, null=True, blank=True, on_delete=models.CASCADE)
    audience = models.ManyToManyField(User, default=[], related_name='+')
    seen_at = models.DateTimeField(null=True, default=None)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    club_has_seen = []

    class Meta:
        constraints = [
            UniqueConstraint(fields=['guild'], condition=Q(seen_at=None),
                             name='unique_guild_seen_at_none')
        ]

    def get_top_movies(self, members_ids: list):
        movies = Movie.objects.filter(guild=self.guild, session__seen_at__gt='2022-01-01')
        suggesters = set(members_ids).difference(set(self.audience.all().values_list('id', flat=True)))
        print(suggesters)
        movies = movies.filter(already_seen__in=suggesters)
        self.club_has_seen = movies.distinct().all()

    @property
    def available_movies(self):
        if self.audience.all():
            return Movie.objects.filter(guild=self.guild, session__seen_at=None).exclude(already_seen__in=self.audience.all()).distinct().all()
        return Movie.objects.filter(guild=self.guild, session__seen_at=None).all()

    @property
    def audience_want_to_see_movies(self):
        if self.audience.all():
            movies = self.audience.first().want_to_see.all()
            for user in self.audience.all():
                movies = movies.intersection(user.want_to_see.all())
            return Movie.objects.filter(id__in=movies.values_list('id',flat=True)).exclude(already_seen__in=self.audience.all())
        return []


class Ranking(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_rankings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_rankings')
    rating = models.IntegerField()

    class Meta:
        unique_together = [['movie', 'user']]

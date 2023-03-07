from django.db import models
from django.db.models import Q

from django.db.models import UniqueConstraint


class Guild(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)


class User(models.Model):
    id = models.IntegerField(primary_key=True)
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
    dont_want_to_watch = models.ManyToManyField(User, blank=True, related_name='dont_want_to_watch')
    rankings = models.ManyToManyField(User, through='Ranking')
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        unique_together = ('uuid', 'guild')

    @property
    def average_rating(self):
        rows = Ranking.objects.filter(movie=self)
        return sum([row.rating for row in rows]) / len(rows) if len(rows) > 0 else None


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
        constraints = [UniqueConstraint(fields=['guild'], condition=Q(seen_at=None), name='unique_guild_seen_at_none')]

    def load_top_movies(self, members_ids: list):
        movies = Movie.objects.filter(guild=self.guild, session__seen_at__gt='2022-01-01')
        audience_ids = set(self.audience.all().values_list('id', flat=True))
        suggesters = set(members_ids).difference(audience_ids)
        movies = movies.filter(Q(session__audience__in=suggesters) & ~Q(dont_want_to_watch__in=audience_ids)).distinct().all()
        output = []
        for movie in movies:
            if set(movie.already_seen.all().values_list('id', flat=True)).isdisjoint(audience_ids):
                output.append(movie)
        self.club_has_seen = sorted(output, reverse=True, key=lambda i: (i.average_rating if i.average_rating else -1))
        return

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
            return Movie.objects.filter(guild=self.guild, id__in=movies.values_list('id',flat=True)).exclude(already_seen__in=self.audience.all())
        return []


class Channel(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE)
    config = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)


class Ranking(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_rankings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_rankings')
    rating = models.IntegerField()

    class Meta:
        unique_together = [['movie', 'user']]


class ChatLog(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='chat_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_logs')
    message = models.CharField(max_length=10000)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)



class Fact(models.Model):
    chat_log = models.ForeignKey(ChatLog, on_delete=models.CASCADE, related_name='facts')
    fact = models.CharField(max_length=500)
    tags = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

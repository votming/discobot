from django.db import models


# Create your models here.
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
    id = models.CharField(primary_key=True, max_length=50)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, unique=True)
    image = models.CharField(max_length=450, default=None, null=True)
    already_seen = models.ManyToManyField(User, blank=True, related_name='+')
    want_to_see = models.ManyToManyField(User, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

#class MovieRanking

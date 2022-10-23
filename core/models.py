from django.db import models


# Create your models here.
class Channel(models.Model):
    id = models.CharField(max_length=30)
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)


class User(models.Model):
    id = models.CharField(max_length=30)
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)


class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    channel = models.ForeignKey(Channel)
    name = models.CharField(max_length=150)
    already_seen = models.ManyToManyField(User)
    want_to_see = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

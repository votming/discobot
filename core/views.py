from django.shortcuts import render
from django.views.generic import TemplateView, ListView

from core.models import Movie


class MovieView(ListView):
    model = Movie

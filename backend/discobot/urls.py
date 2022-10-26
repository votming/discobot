from django.contrib import admin
from django.urls import path, include

from core.views.guilds import GuildsViewSet
from core.views.movies import MoviesViewSet
from core.views.sessions import SessionsViewSet

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/guild', GuildsViewSet.as_view({'post': 'create'})),

    path('api/session', SessionsViewSet.as_view({'post': 'create'})),
    path('api/session/by_guild/<guild_id>', SessionsViewSet.as_view({'get': 'list'})),
    path('api/session/<pk>', SessionsViewSet.as_view({'get': 'retrieve'})),
    path('api/session/<pk>/join', SessionsViewSet.as_view({'post': 'join_session'})),
    path('api/session/<pk>/leave', SessionsViewSet.as_view({'post': 'leave_session'})),
    path('api/session/<pk>/select_random', SessionsViewSet.as_view({'get': 'select_random'})),
    path('api/session/<pk>/select_movie', SessionsViewSet.as_view({'post': 'select_movie'})),
    path('api/session/<pk>/decline_movie', SessionsViewSet.as_view({'get': 'decline_movie'})),
    path('api/session/<pk>/finish', SessionsViewSet.as_view({'get': 'finish_session'})),

    path('api/movie', MoviesViewSet.as_view({'post': 'create'})),
    path('api/movie/get', MoviesViewSet.as_view({'post': 'get_movie'})),
    path('api/movie/subscribe_to_watch', MoviesViewSet.as_view({'post': 'subscribe_to_watch'})),
    path('api/movie/watched', MoviesViewSet.as_view({'post': 'set_watched'})),
    path('api/movie/unwatched', MoviesViewSet.as_view({'post': 'set_unwatched'})),
    path('api/movie/rate', MoviesViewSet.as_view({'post': 'rate_movie'})),
]

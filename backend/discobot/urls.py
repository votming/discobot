from django.contrib import admin
from django.urls import path, include

from core.serializers import FactSerializer
from core.views.channel import ChannelViewSet
from core.views.chat_log import ChatLogViewSet, FactViewSet
from core.views.guilds import GuildsViewSet
from core.views.movies import MoviesViewSet
from core.views.sessions import SessionsViewSet
from core.views.user import UserViewSet

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/guild', GuildsViewSet.as_view({'post': 'create'})),
    path('api/handshake', GuildsViewSet.as_view({'get': 'handshake'})),

    path('api/channel', ChannelViewSet.as_view({'post': 'create'})),
    path('api/channel/<pk>', ChannelViewSet.as_view({'get': 'retrieve', 'patch': 'update'})),

    path('api/chat_log', ChatLogViewSet.as_view({'get': 'retrieve', 'post': 'create'})),
    path('api/chat_log/facts', FactViewSet.as_view({'get': 'retrieve', 'post': 'create'})),
    path('api/chat_log/<pk>', ChatLogViewSet.as_view({'get': 'retrieve'})),

    path('api/user/<pk>/facts', UserViewSet.as_view({'get': 'get_facts', 'post': 'create'})),

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
    path('api/movie/dont_want_to_watch', MoviesViewSet.as_view({'post': 'dont_want_to_watch'})),
    path('api/movie/watched', MoviesViewSet.as_view({'post': 'set_watched'})),
    path('api/movie/unwatched', MoviesViewSet.as_view({'post': 'set_unwatched'})),
    path('api/movie/rate', MoviesViewSet.as_view({'post': 'rate_movie'})),
]

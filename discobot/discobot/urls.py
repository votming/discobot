from django.contrib import admin
from django.urls import path, include
from core.views import MoviesViewSet, GuildsViewSet

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/guild', GuildsViewSet.as_view({'post': 'create'})),
    path('api/movie', MoviesViewSet.as_view({'post': 'create'})),
    path('api/movie/by_name/<name>', MoviesViewSet.as_view({'get': 'get_by_name'})),
    path('api/movie/<pk>', MoviesViewSet.as_view({'get': 'retrieve'})),
    path('api/movie/<pk>/subscribe_to_watch', MoviesViewSet.as_view({'post': 'subscribe_to_watch'})),
    path('api/movie/<pk>/watched', MoviesViewSet.as_view({'post': 'set_watched'})),
]

from django.contrib import admin
from django.urls import path
from core.views import MovieView

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'^User/(?P<userid>\d+)/$', MovieView.as_view(template_name="about.html"))
]

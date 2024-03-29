#!/usr/bin/python3

"""moundmusic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please
see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path

from moundmusic import views

urlpatterns = [
    path("", views.site_index),
    # /admin isn't supported because this package shares model classes
    # between apps, which makes it impossible to register them with
    # django.contrib.admin
    path("albums", include("albums.urls")),
    path("albums/", include("albums.urls")),
    path("artists", include("artists.urls")),
    path("artists/", include("artists.urls")),
    path("genres", include("genres.urls")),
    path("genres/", include("genres.urls")),
    path("songs", include("songs.urls")),
    path("songs/", include("songs.urls")),
    path("users", include("users.urls")),
    path("users/", include("users.urls")),
]

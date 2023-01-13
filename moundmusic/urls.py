#!/usr/bin/python3

"""moundmusic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
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
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('albums/', include('albums.urls')),
    path('albums', include('albums.urls')),
    path('artists/', include('artists.urls')),
    path('artists', include('artists.urls')),
    path('buyers', include('buyers.urls')),
    path('buyers/', include('buyers.urls')),
    path('genres', include('genres.urls')),
    path('genres/', include('genres.urls')),
    path('sellers', include('sellers.urls')),
    path('sellers/', include('sellers.urls')),
    path('songs', include('songs.urls')),
    path('songs/', include('songs.urls')),
    path('users', include('users.urls')),
    path('users/', include('users.urls')),
    path('admin/', admin.site.urls)
]


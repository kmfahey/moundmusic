#!/usr/bin/python3

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:album_id>', views.single_album),
    path('<int:album_id>/songs', views.single_album_songs),
    path('<int:album_id>/songs/<int:song_id>', views.single_album_single_song),
    path('<int:album_id>/genres', views.single_album_genres),
    path('<int:album_id>/genres/<int:genre_id>', views.single_album_single_genre),
]

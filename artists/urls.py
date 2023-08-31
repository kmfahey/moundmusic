#!/usr/bin/python3

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:model_obj_id>", views.single_artist),
    path("<int:outer_model_obj_id>/albums", views.single_artist_albums),
    path(
        "<int:outer_model_obj_id>/albums/<int:inner_model_obj_id>",
        views.single_artist_single_album,
    ),
    path("<int:outer_model_obj_id>/songs", views.single_artist_songs),
    path(
        "<int:outer_model_obj_id>/songs/<int:inner_model_obj_id>",
        views.single_artist_single_song,
    ),
    path("<int:outer_model_obj_id>/genres", views.single_artist_genres),
    path(
        "<int:outer_model_obj_id>/genres/<int:inner_model_obj_id>",
        views.single_artist_single_genre,
    ),
]

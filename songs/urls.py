#!/usr/bin/python3

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:model_obj_id>', views.single_song),
    path('<int:outer_model_obj_id>/albums', views.single_song_albums),
    path('<int:outer_model_obj_id>/albums/<int:inner_model_obj_id>', views.single_song_single_album),
    path('<int:outer_model_obj_id>/artists', views.single_song_artists),
    path('<int:outer_model_obj_id>/artists/<int:inner_model_obj_id>', views.single_song_single_artist),
    path('<int:outer_model_obj_id>/genres', views.single_song_genres),
    path('<int:outer_model_obj_id>/genres/<int:inner_model_obj_id>', views.single_song_single_genre),
]

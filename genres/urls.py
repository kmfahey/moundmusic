#!/usr/bin/python3

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:model_obj_id>', views.single_genre),
    path('<int:outer_model_obj_id>/albums', views.single_genre_albums),
    path('<int:outer_model_obj_id>/albums/<int:inner_model_obj_id>', views.single_genre_single_album),
    path('<int:outer_model_obj_id>/songs', views.single_genre_songs),
    path('<int:outer_model_obj_id>/songs/<int:inner_model_obj_id>', views.single_genre_single_song),
    path('<int:outer_model_obj_id>/artists', views.single_genre_artists),
    path('<int:outer_model_obj_id>/artists/<int:inner_model_obj_id>', views.single_genre_single_artist),
]

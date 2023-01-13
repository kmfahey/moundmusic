#!/usr/bin/python3

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:model_obj_id>', views.single_album),
    path('<int:outer_model_obj_id>/artists', views.single_album_artists),
    path('<int:outer_model_obj_id>/artists/<int:inner_model_obj_id>', views.single_album_single_artist),
    path('<int:outer_model_obj_id>/songs', views.single_album_songs),
    path('<int:outer_model_obj_id>/songs/<int:inner_model_obj_id>', views.single_album_single_song),
    path('<int:outer_model_obj_id>/genres', views.single_album_genres),
    path('<int:outer_model_obj_id>/genres/<int:inner_model_obj_id>', views.single_album_single_genre),
]

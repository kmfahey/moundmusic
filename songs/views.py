#!/usr/bin/python

from django.http.response import JsonResponse
from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework import status

from moundmusic.viewutils import validate_bridged_table_column_value_pair
from moundmusic.viewutils import define_GET_POST_index_closure, define_single_model_GET_PATCH_DELETE_closure, \
        define_single_outer_model_all_of_inner_model_GET_POST_closure, \
        define_single_outer_model_single_inner_model_GET_DELETE_closure

from .models import Album, Artist, Genre, Song, AlbumSongBridge, ArtistSongBridge, SongGenreBridge


# GET,POST          /artists
index = define_GET_POST_index_closure(Song)


# GET,PATCH,DELETE  /songs/<song_id>
single_song = define_single_model_GET_PATCH_DELETE_closure(Song, 'song_id')


# GET               /songs/<song_id>/albums
@api_view(['GET'])
def single_song_albums(request, outer_model_obj_id):
    try:
        Song.objects.get(song_id=outer_model_obj_id)
    except Song.DoesNotExist:
        return JsonResponse({'message': f'no song with song_id={outer_model_obj_id}'},
                            status=status.HTTP_404_NOT_FOUND)
    bridge_rows = AlbumSongBridge.objects.filter(song_id=outer_model_obj_id)
    return_list = [{'disc_number':bridge_row.disc_number,
                    'track_number':bridge_row.track_number,
                    'album':Album.objects.get(album_id=bridge_row.album_id).serialize()}
                   for bridge_row in bridge_rows]
    return JsonResponse(return_list, status=status.HTTP_200_OK, safe=False)


# GET               /songs/<song_id>/albums/<album_id>
@api_view(['GET'])
def single_song_single_album(request, outer_model_obj_id, inner_model_obj_id):
    result = validate_bridged_table_column_value_pair(Song, 'song_id', outer_model_obj_id,
                                                      Album, 'album_id', inner_model_obj_id,
                                                      AlbumSongBridge)
    if isinstance(result, JsonResponse):
        return result
    else:
        _, inner_model, _ = result
    bridge_row = AlbumSongBridge.objects.get(song_id=outer_model_obj_id, album_id=inner_model_obj_id)
    retval = {'track_number':bridge_row.track_number,
              'disc_number':bridge_row.disc_number,
              'album':inner_model.serialize()}
    return JsonResponse(retval, status=status.HTTP_200_OK)


# GET,POST          /songs/<song_id>/artists
single_song_artists = define_single_outer_model_all_of_inner_model_GET_POST_closure(Song, 'song_id', Artist, 'artist_id', ArtistSongBridge)


# GET,DELETE  /songs/<song_id>/artists/<artist_id>
single_song_single_artist = define_single_outer_model_single_inner_model_GET_DELETE_closure(Song, 'song_id', Artist, 'artist_id', ArtistSongBridge)


# GET,POST          /songs/<song_id>/genres
single_song_genres = define_single_outer_model_all_of_inner_model_GET_POST_closure(Song, 'song_id', Genre, 'genre_id', SongGenreBridge)


# GET,DELETE  /songs/<song_id>/genres/<genre_id>
single_song_single_genre = define_single_outer_model_single_inner_model_GET_DELETE_closure(Song, 'song_id', Genre, 'genre_id', SongGenreBridge)


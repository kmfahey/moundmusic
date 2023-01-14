#!/usr/bin/python

from operator import itemgetter

from django.http.response import JsonResponse

from rest_framework import status
from rest_framework.decorators import api_view

from json import loads as parse_json
from json.decoder import JSONDecodeError

from .models import Album, AlbumSongBridge, Genre, AlbumGenreBridge, Song, Artist, ArtistAlbumBridge

from moundmusic.viewutils import dispatch_funcs_by_method, validate_post_request, \
        validate_patch_request, validate_bridged_table_column_value_pair

from moundmusic.viewutils import define_GET_POST_index_closure, define_single_model_GET_PATCH_DELETE_closure, \
        define_single_outer_model_all_of_inner_model_GET_POST_closure, \
        define_single_outer_model_single_inner_model_GET_DELETE_closure


# GET    — The most common option, returns some data from the API based on the
#          endpoint you visit and any parameters you provide
#
# POST   — Creates a new record that gets appended to the database
#
# DELETE — Deletes the record at the given URI
#
# PATCH  — Update individual fields of a record

# Create your views here.


# GET,POST          /albums/
index = define_GET_POST_index_closure(Album, 'album_id')


# GET,PATCH,DELETE  /albums/<int:model_obj_id>/
single_album = define_single_model_GET_PATCH_DELETE_closure(Album, 'album_id')


# GET               /albums/<int:model_obj_id>/songs
@api_view(['GET'])
def single_album_songs(request, outer_model_obj_id):
    bridge_rows = AlbumSongBridge.objects.filter(album_id=outer_model_obj_id)
    if not len(bridge_rows):
        return JsonResponse({'message': f'no songs with album_id={outer_model_obj_id}'}, status=status.HTTP_404_NOT_FOUND)
    return_struct = dict()
    rows_by_disc_and_track_numbers = {(bridge_row.disc_number, bridge_row.track_number): bridge_row
                                      for bridge_row in bridge_rows}
    for disc_number in map(itemgetter(0), rows_by_disc_and_track_numbers.keys()):
        return_struct["disc_%i" % disc_number] = dict()
    for (disc_number, track_number), bridge_row in sorted(rows_by_disc_and_track_numbers.items()):
        disc_key = "disc_%i" % disc_number
        track_key = "track_%i" % track_number
        return_struct[disc_key][track_key] = Song.objects.get(song_id=bridge_row.song_id).serialize()
    return JsonResponse(return_struct, status=status.HTTP_200_OK)


# GET,DELETE        /albums/<int:model_obj_id>/songs/<int:song_id>
single_album_single_song = define_single_outer_model_single_inner_model_GET_DELETE_closure(
                                   Album, 'album_id', Song, 'song_id', AlbumSongBridge)


# GET,POST          /albums/<int:model_obj_id>/genres
single_album_genres = define_single_outer_model_all_of_inner_model_GET_POST_closure(
                              Album, 'album_id', Genre, 'genre_id', AlbumGenreBridge)


# GET,DELETE        /albums/<int:model_obj_id>/genres/<int:genre_id>
single_album_single_genre = define_single_outer_model_single_inner_model_GET_DELETE_closure(
                                    Album, 'album_id', Genre, 'genre_id', AlbumGenreBridge)


# GET,POST          /albums/<int:model_obj_id>/artists/
single_album_artists = define_single_outer_model_all_of_inner_model_GET_POST_closure(
                               Album, 'album_id', Artist, 'artist_id', ArtistAlbumBridge)


# GET,DELETE        /albums/<int:model_obj_id>/artists/<int:artist_id>/
single_album_single_artist = define_single_outer_model_single_inner_model_GET_DELETE_closure(
                                     Album, 'album_id', Artist, 'artist_id', ArtistAlbumBridge)


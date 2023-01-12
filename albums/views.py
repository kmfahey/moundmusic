#!/usr/bin/python

from operator import itemgetter

from collections import defaultdict

from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from json import loads as parse_json
from json.decoder import JSONDecodeError

from datetime import date

from .models import Album, AlbumSongBridge, Genre, AlbumGenreBridge, Song, Artist, ArtistAlbumBridge

from moundmusic.viewutils import dispatch_funcs_by_method, validate_input, validate_post_request, \
        validate_patch_request, validate_bridged_table_column_value_pair


# GET    — The most common option, returns some data from the API based on the
#          endpoint you visit and any parameters you provide
#
# POST   — Creates a new record that gets appended to the database
#
# DELETE — Deletes the record at the given URI
#
# PATCH  — Update individual fields of a record

# Create your views here.

@api_view(['GET', 'POST'])
def index(request):

    def _index_GET():
        return JsonResponse([album.serialize() for album in Album.objects.all()],
                            status=status.HTTP_200_OK, safe=False)

    def _index_POST():
        result = validate_post_request(request, Album)
        if isinstance(result, JsonResponse):
            return result
        else:
            validated_args = result
        new_album = Album(**validated_args)
        new_album.save()
        return JsonResponse(new_album.serialize(), status=status.HTTP_201_CREATED)

    return dispatch_funcs_by_method((_index_GET, _index_POST), request)


@api_view(['GET', 'PATCH', 'DELETE'])
def single_album(request, album_id):

    def _single_album_GET():
        try:
            album = Album.objects.get(album_id=album_id)
        except Album.DoesNotExist:
            return JsonResponse({'message':f'no album with album_id={album_id}'}, status=status.HTTP_404_NOT_FOUND)
        return JsonResponse(album.serialize(), status=status.HTTP_200_OK)

    def _single_album_PATCH():
        retval = validate_patch_request(request, Album, 'album_id', album_id)
        if isinstance(retval, JsonResponse):
            return retval
        else:
            album, validated_input = retval
        for column, column_value in validated_input.items():
            setattr(album, column, column_value)
        album.save()
        return JsonResponse(album.serialize(), status=status.HTTP_200_OK)

    def _single_album_DELETE():
        try:
            album = Album.objects.get(album_id=album_id)
        except Album.DoesNotExist:
            return JsonResponse({'message':f'no album with album_id={album_id}'}, status=status.HTTP_404_NOT_FOUND)
        album.delete()
        return JsonResponse({'message':f'album with album_id={album_id} deleted'}, status=status.HTTP_200_OK)

    return dispatch_funcs_by_method((_single_album_GET, _single_album_PATCH, _single_album_DELETE), request)


@api_view(['GET'])
def single_album_songs(request, album_id):
    bridge_rows = AlbumSongBridge.objects.filter(album_id=album_id)
    if not len(bridge_rows):
        return JsonResponse({'message':f'no songs with album_id={album_id}'}, status=status.HTTP_404_NOT_FOUND)
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


@api_view(['GET', 'PATCH', 'DELETE'])
def single_album_single_song(request, album_id, song_id):

    def _single_album_single_song_GET():
        result = validate_bridged_table_column_value_pair(Album, 'album_id', album_id,
                                                          Song, 'song_id', song_id,
                                                          AlbumSongBridge)
        if isinstance(result, JsonResponse):
            return result
        else:
            _, song, _ = result
        return JsonResponse(song.serialize(), status=status.HTTP_200_OK)

    def _single_album_single_song_PATCH():
        result = validate_bridged_table_column_value_pair(Album, 'album_id', album_id,
                                                          Song, 'song_id', song_id,
                                                          AlbumSongBridge)
        if isinstance(result, JsonResponse):
            return result
        retval = validate_patch_request(request, Song, 'song_id', song_id)
        if isinstance(retval, JsonResponse):
            return retval
        else:
            song, validated_input = retval
        for column, column_value in validated_input.items():
            setattr(song, column, column_value)
        song.save()
        return JsonResponse(song.serialize(), status=status.HTTP_200_OK)

    return dispatch_funcs_by_method((_single_album_single_song_GET,
                                      _single_album_single_song_PATCH),
                                     request)


@api_view(['GET', 'POST'])
def single_album_genres(request, album_id):

    def _single_album_genres_GET():
        try:
            Album.objects.get(album_id=album_id)
        except Album.DoesNotExist:
            return JsonResponse({'message':f'no album with album_id={album_id}'}, status=status.HTTP_404_NOT_FOUND)
        bridge_rows = AlbumGenreBridge.objects.filter(album_id=album_id)
        return_list = [Genre.objects.get(genre_id=bridge_row.genre_id).serialize() for bridge_row in bridge_rows]
        return JsonResponse(return_list, status=status.HTTP_200_OK, safe=False)

    def _single_album_genres_POST():
        try:
            Album.objects.get(album_id=album_id)
        except Album.DoesNotExist:
            return JsonResponse({'message':f'no album with album_id={album_id}'}, status=status.HTTP_404_NOT_FOUND)
        try:
            posted_json = parse_json(request.body)
        except JSONDecodeError as exception:
            return JsonResponse({'message':exception.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        diff = set(posted_json.keys()) - set(('genre_id',))
        if diff:
            prop_expr = ', '.join(f"'{property}'" for property in diff)
            return JsonResponse({'message':f'unexpected propert{"ies" if len(diff) > 1 else "y"} in input: {prop_expr}'},
                                status=status.HTTP_400_BAD_REQUEST)
        genre_id = posted_json['genre_id']
        try:
            genre = Genre.objects.get(genre_id=genre_id)
        except Genre.DoesNotExist:
            return JsonResponse({'message':f'no genre with genre_id={genre_id}'}, status=status.HTTP_404_NOT_FOUND)
        try:
            bridge_row = AlbumGenreBridge.objects.get(album_id=album_id, genre_id=genre_id)
        except AlbumGenreBridge.DoesNotExist:
            pass
        else:
            return JsonResponse({'message':f'association between album with album_id={album_id} '
                                          f'and genre with genre_id={genre_id} already exists'},
                                status=status.HTTP_400_BAD_REQUEST)
        bridge_row = AlbumGenreBridge(album_id=album_id, genre_id=genre_id)
        bridge_row.save()
        return JsonResponse(genre.serialize(), status=status.HTTP_200_OK)

    return dispatch_funcs_by_method((_single_album_genres_GET,
                                      _single_album_genres_POST), request)


@api_view(['GET', 'DELETE'])
def single_album_single_genre(request, album_id, genre_id):

    def _single_album_single_genre_GET():
        result = validate_bridged_table_column_value_pair(Album, 'album_id', album_id,
                                                          Genre, 'genre_id', genre_id,
                                                          AlbumGenreBridge)
        if isinstance(result, JsonResponse):
            return result
        else:
            _, genre, _ = result
        return JsonResponse(genre.serialize(), status=status.HTTP_200_OK)

    def _single_album_single_genre_DELETE():
        result = validate_bridged_table_column_value_pair(Album, 'album_id', album_id,
                                                          Genre, 'genre_id', genre_id,
                                                          AlbumGenreBridge)
        if isinstance(result, JsonResponse):
            return result
        else:
            _, _, bridge_row = result
        bridge_row.delete()
        return JsonResponse({'message':f'association between album with album_id={album_id} '
                                       f'and genre with genre_id={genre_id} deleted'},
                            status=status.HTTP_200_OK)

    return dispatch_funcs_by_method((_single_album_single_genre_GET,
                                      _single_album_single_genre_DELETE), request)


@api_view(['GET', 'POST'])
def single_album_artists(request, album_id):

    def _single_album_artists_GET():
        try:
            Album.objects.get(album_id=album_id)
        except Album.DoesNotExist:
            return JsonResponse({'message':f'no album with album_id={album_id}'}, status=status.HTTP_404_NOT_FOUND)
        bridge_rows = ArtistAlbumBridge.objects.filter(album_id=album_id)
        if not len(bridge_rows):
            return JsonResponse({'message':f'no artists associated with album_id={album_id}'},
                                status=status.HTTP_404_NOT_FOUND)
        artists = [Artist.objects.get(artist_id=bridge_row.artist_id) for bridge_row in bridge_rows]
        return JsonResponse([artist.serialize() for artist in artists],
                            status=status.HTTP_200_OK, safe=False)

    def _single_album_artists_POST():
        try:
            Album.objects.get(album_id=album_id)
        except Album.DoesNotExist:
            return JsonResponse({'message':f'no album with album_id={album_id}'}, status=status.HTTP_404_NOT_FOUND)
        result = validate_post_request(request, Artist, all_nullable=True)
        if isinstance(result, JsonResponse):
            return result
        else:
            validated_args = result
        diff = set(validated_args.keys()) - {'artist_id'}
        if diff:
            diff_expr = ', '.join(f"'{key}'" for key in diff)
            return JsonResponse({'message':f'unexpected propert{"ies" if len(diff) > 1 else "y"} in input: {diff_expr}'},
                               status=status.HTTP_400_BAD_REQUEST)
        artist_id = validated_args['artist_id']
        try:
            artist = Artist.objects.get(artist_id=artist_id)
        except Artist.DoesNotExist:
            return JsonResponse({'message':f'no artist with artist_id={artist_id}'},
                                status=status.HTTP_404_NOT_FOUND)
        try:
            bridge_row = ArtistAlbumBridge.objects.get(artist_id=artist_id, album_id=album_id)
        except ArtistAlbumBridge.DoesNotExist:
            pass
        else:
            return JsonResponse({'message':f'association between artist with artist_id={artist_id} '
                                          f'and album with album_id={album_id} already exists'},
                               status=status.HTTP_400_BAD_REQUEST)
        bridge_row = ArtistAlbumBridge(artist_id=artist_id, album_id=album_id)
        bridge_row.save()
        return JsonResponse(artist.serialize(), status=status.HTTP_201_CREATED)

    return dispatch_funcs_by_method((_single_album_artists_GET, _single_album_artists_POST), request)


@api_view(['GET', 'DELETE'])
def single_album_single_artist(request, album_id, artist_id):

    def _single_album_single_artist_GET():
        result = validate_bridged_table_column_value_pair(Album, 'album_id', album_id,
                                                          Artist, 'artist_id', artist_id,
                                                          ArtistAlbumBridge)
        if isinstance(result, JsonResponse):
            return result
        else:
            _, artist, _ = result
        return JsonResponse(artist.serialize(), status=status.HTTP_200_OK)

    def _single_album_single_artist_DELETE():
        result = validate_bridged_table_column_value_pair(Album, 'album_id', album_id,
                                                          Artist, 'artist_id', artist_id,
                                                          ArtistAlbumBridge)
        if isinstance(result, JsonResponse):
            return result
        else:
            _, _, bridge_row = result
        bridge_row.delete()
        return JsonResponse({'message':f'association between album with album_id={album_id} '
                                       f'and artist with artist_id={artist_id} deleted'},
                            status=status.HTTP_200_OK)

    return dispatch_funcs_by_method((_single_album_single_artist_GET,
                                      _single_album_single_artist_DELETE),
                                     request)



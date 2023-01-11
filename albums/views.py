#!/usr/bin/python

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

from .models import Album, AlbumSongBridge, Genre, AlbumGenreBridge, Song


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
        try:
            posted_json = parse_json(request.body)
        except JSONDecodeError:
            return JsonResponse({'message':'JSON did not parse'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validatedArgs = Album.validate_input(posted_json)
        except ValueError as exception:
            return JsonResponse({'message':exception.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        new_album = Album(**validatedArgs)
        new_album.save()
        return JsonResponse(new_album.serialize(), status=status.HTTP_201_CREATED)

    return _dispatch_funcs_by_method((_index_GET, _index_POST), request)



def _validate_patch_request(request, model_class, model_id_attr_name, model_id_attr_val):
    try:
        model_instance = model_class.objects.get(**{model_id_attr_name: model_id_attr_val})
    except Album.DoesNotExist:
        return JsonResponse({'message':f'no record with {model_id_attr_name}={model_id_attr_val}'}, status=status.HTTP_404_NOT_FOUND)
    try:
        posted_json = parse_json(request.body)
    except JSONDecodeError as exception:
        return JsonResponse({'message':exception.args[0]}, status=status.HTTP_400_BAD_REQUEST)
    if not len(posted_json):
        return JsonResponse({'message':'empty JSON object'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        validated_input = model_class.validate_input(posted_json, all_nullable=True)
    except ValueError as exception:
        return JsonResponse({'message':exception.args[0]}, status=status.HTTP_400_BAD_REQUEST)
    return model_instance, validated_input


@api_view(['GET', 'PATCH', 'DELETE'])
def single_album(request, album_id):

    def _single_album_GET():
        try:
            album = Album.objects.get(album_id=album_id)
        except Album.DoesNotExist:
            return JsonResponse({'message':f'no record with album_id={album_id}'}, status=status.HTTP_404_NOT_FOUND)
        return JsonResponse(album.serialize(), status=status.HTTP_200_OK)

    def _single_album_PATCH():
        retval = _validate_patch_request(request, Album, 'album_id', album_id)
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
            return JsonResponse({'message':f'no record with album_id={album_id}'}, status=status.HTTP_404_NOT_FOUND)
        album.delete()
        return JsonResponse({'message':f'album record with album_id={album_id} deleted'}, status=status.HTTP_200_OK)

    return _dispatch_funcs_by_method((_single_album_GET, _single_album_PATCH, _single_album_DELETE), request)


@api_view(['GET'])
def single_album_songs(request, album_id):
    try:
        bridge_rows = AlbumSongBridge.objects.filter(album_id=album_id)
    except AlbumSongBridge.DoesNotExist:
        return JsonResponse({'message':f'no songs with album_id={album_id}'}, status=status.HTTP_404_NOT_FOUND)
    return_struct = dict()
    rows_by_disc_and_track_numbers = dict()
    for bridge_row in bridge_rows:
        rows_by_disc_and_track_numbers[bridge_row.disc_number, bridge_row.track_number] = bridge_row
    disc_numbers = sorted(set(disc_number for disc_number, _ in rows_by_disc_and_track_numbers.keys()))
    for disc_number in disc_numbers:
        return_struct["disc_%i" % disc_number] = dict()
    for (disc_number, track_number), bridge_row in sorted(rows_by_disc_and_track_numbers.items()):
        disc_key = "disc_%i" % disc_number
        track_key = "track_%i" % track_number
        return_struct[disc_key][track_key] = Song.objects.get(song_id=bridge_row.song_id).serialize()
    return JsonResponse(return_struct, status=status.HTTP_200_OK)


@api_view(['GET', 'PATCH', 'DELETE'])
def single_album_single_song(request, album_id, song_id):

    def _single_album_single_song_GET():
        try:
            bridge_row = AlbumSongBridge.objects.get(album_id=album_id, song_id=song_id)
        except AlbumSongBridge.DoesNotExist:
            return JsonResponse({'message':f'album with album_id={album_id} has no song with song_id={song_id}'}, status=status.HTTP_404_NOT_FOUND)
        song = Song.objects.get(song_id=song_id)
        return JsonResponse(song.serialize(), status=status.HTTP_200_OK)

    def _single_album_single_song_PATCH():
        try:
            bridge_row = AlbumSongBridge.objects.get(album_id=album_id, song_id=song_id)
        except AlbumSongBridge.DoesNotExist:
            return JsonResponse({'message':f'album with album_id={album_id} has no song with song_id={song_id}'}, status=status.HTTP_404_NOT_FOUND)
        retval = _validate_patch_request(request, Song, 'song_id', song_id)
        if isinstance(retval, JsonResponse):
            return retval
        else:
            song, validated_input = retval
        for column, column_value in validated_input.items():
            setattr(song, column, column_value)
        song.save()
        return JsonResponse(song.serialize(), status=status.HTTP_200_OK)

    def _single_album_single_song_DELETE():
        try:
            bridge_row = AlbumSongBridge.objects.get(album_id=album_id, song_id=song_id)
        except AlbumSongBridge.DoesNotExist:
            return JsonResponse({'message':f'album with album_id={album_id} has no song with song_id={song_id}'}, status=status.HTTP_404_NOT_FOUND)
        song = Song.objects.get(song_id=song_id)
        song.delete()
        return JsonResponse({'message':f'song record with album_id={album_id} and song_id={song_id} deleted'}, status=status.HTTP_200_OK)

    return _dispatch_funcs_by_method((_single_album_single_song_GET,
                                      _single_album_single_song_PATCH,
                                      _single_album_single_song_DELETE),
                                     request)


@api_view(['GET', 'POST'])
def single_album_genres(request, album_id):

    def _single_album_genres_GET():
        try:
            bridge_rows = AlbumGenreBridge.objects.filter(album_id=album_id)
        except AlbumSongBridge.DoesNotExist:
            return JsonResponse({'message':f'no songs with album_id={album_id}'}, status=status.HTTP_404_NOT_FOUND)
        return_list = [Genre.objects.get(genre_id=bridge_row.genre_id).serialize() for bridge_row in bridge_rows]
        return JsonResponse(return_list, status=status.HTTP_200_OK, safe=False)

    def _single_album_genres_POST():
        try:
            posted_json = parse_json(request.body)
        except JSONDecodeError as exception:
            return JsonResponse({'message':exception.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        difference = set(posted_json.keys()) - set(('genre_id',))
        if difference:
            prop_expr = ', '.join(f"'{property}'" for property in difference)
            return JsonResponse({'message':f'unexpected properties: {prop_expr}'}, status=status.HTTP_400_BAD_REQUEST)
        genre_id = posted_json['genre_id']
        try:
            genre = Genre.objects.get(genre_id=genre_id)
        except Genre.DoesNotExist:
            return JsonResponse({'message':f'no genre with genre_id={genre_id}'}, status=status.HTTP_404_NOT_FOUND)
        bridge_row = AlbumGenreBridge(album_id=album_id, genre_id=genre_id)
        bridge_row.save()
        return JsonResponse(genre.serialize(), status=status.HTTP_200_OK)

    return _dispatch_funcs_by_method((_single_album_genres_GET,
                                      _single_album_genres_POST), request)


@api_view(['GET', 'DELETE'])
def single_album_single_genre(request, album_id, genre_id):

    def _single_album_single_genre_GET():
        try:
            bridge_row = AlbumGenreBridge.objects.get(album_id=album_id, genre_id=genre_id)
        except AlbumGenreBridge.DoesNotExist:
            return JsonResponse({'message':f'album with album_id={album_id} has no genre with genre_id={genre_id}'}, status=status.HTTP_404_NOT_FOUND)
        genre = Genre.objects.get(genre_id=genre_id)
        return JsonResponse(genre.serialize(), status=status.HTTP_200_OK)

    def _single_album_single_genre_DELETE():
        try:
            bridge_row = AlbumGenreBridge.objects.get(album_id=album_id, genre_id=genre_id)
        except AlbumGenreBridge.DoesNotExist:
            return JsonResponse({'message':f'album with album_id={album_id} has no genre with genre_id={genre_id}'}, status=status.HTTP_404_NOT_FOUND)
        bridge_row.delete()
        return JsonResponse({'message':f'association between album record with album_id={album_id} and genre record with genre_id={genre_id} deleted'}, status=status.HTTP_200_OK)

    return _dispatch_funcs_by_method((_single_album_single_genre_GET,
                                      _single_album_single_genre_DELETE), request)


def _dispatch_funcs_by_method(functions, request):
    dispatch_table = dict()
    for function in functions:
        func_name = function.__name__
        _, method = func_name.rsplit('_', 1)
        dispatch_table[method] = function
    method = request.method
    if method in dispatch_table:
        return dispatch_table[method]()
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


#!/usr/bin/python

from django.http.response import JsonResponse

from rest_framework.decorators import api_view
from rest_framework import status

from moundmusic.viewutils import dispatch_funcs_by_method, validate_post_request, \
        validate_bridged_table_column_value_pair
from moundmusic.viewutils import define_GET_POST_index_closure, define_single_model_GET_PATCH_DELETE_closure, \
        define_single_outer_model_all_of_inner_model_GET_POST_closure, \
        define_single_outer_model_single_inner_model_GET_DELETE_closure

from .models import Album, Artist, Genre, Song, AlbumSongBridge, ArtistSongBridge, SongGenreBridge, SongLyrics


# GET,POST          /artists
index = define_GET_POST_index_closure(Song, 'song_id')


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
    return_list = [{'disc_number': bridge_row.disc_number,
                    'track_number': bridge_row.track_number,
                    'album': Album.objects.get(album_id=bridge_row.album_id).serialize()}
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
    retval = {'track_number': bridge_row.track_number,
              'disc_number': bridge_row.disc_number,
              'album': inner_model.serialize()}
    return JsonResponse(retval, status=status.HTTP_200_OK)


# GET,POST          /songs/<song_id>/artists
single_song_artists = define_single_outer_model_all_of_inner_model_GET_POST_closure(Song, 'song_id',
                                                                                    Artist, 'artist_id',
                                                                                    ArtistSongBridge)


# GET,DELETE  /songs/<song_id>/artists/<artist_id>
single_song_single_artist = define_single_outer_model_single_inner_model_GET_DELETE_closure(Song, 'song_id',
                                                                                            Artist, 'artist_id',
                                                                                            ArtistSongBridge)


# GET,POST          /songs/<song_id>/genres
single_song_genres = define_single_outer_model_all_of_inner_model_GET_POST_closure(Song, 'song_id',
                                                                                   Genre, 'genre_id',
                                                                                   SongGenreBridge)


# GET,DELETE  /songs/<song_id>/genres/<genre_id>
single_song_single_genre = define_single_outer_model_single_inner_model_GET_DELETE_closure(Song, 'song_id',
                                                                                           Genre, 'genre_id',
                                                                                           SongGenreBridge)


# GET,POST          /songs/<song_id>/lyrics
@api_view(['GET', 'POST'])
def single_song_lyrics(request, outer_model_obj_id):

    def _single_song_lyrics_GET():
        try:
            Song.objects.get(song_id=outer_model_obj_id)
        except Song.DoesNotExist:
            return JsonResponse({'message': f'no song with song_id={outer_model_obj_id}'},
                                status=status.HTTP_404_NOT_FOUND)
        try:
            song_lyrics = SongLyrics.objects.get(song_id=outer_model_obj_id)
        except SongLyrics.DoesNotExist:
            return JsonResponse({'message': f'no song lyrics associated with song with song_id={outer_model_obj_id}'},
                                status=status.HTTP_404_NOT_FOUND)
        return JsonResponse(song_lyrics.serialize(), status=status.HTTP_200_OK, safe=False)

    def _single_song_lyrics_POST():
        try:
            song = Song.objects.get(song_id=outer_model_obj_id)
        except Song.DoesNotExist:
            return JsonResponse({'message': f'no song with song_id={outer_model_obj_id}'},
                                status=status.HTTP_404_NOT_FOUND)
        if song.song_lyrics_id is not None:
            try:
                song_lyrics = SongLyrics.objects.get(song_lyrics_id=song.song_lyrics_id)
            except SongLyrics.DoesNotExist:
                pass
            else:
                return JsonResponse({'message': f'song with song_id={outer_model_obj_id} already has song lyrics with '
                                                f'song_lyrics_id={song.song_lyrics_id} associated with it'},
                                    status=status.HTTP_409_CONFLICT)
        result = validate_post_request(request, SongLyrics)
        if isinstance(result, JsonResponse):
            return result
        validated_input = result
        song_lyrics = SongLyrics(**validated_input)
        # For no obvious reason, attempting to save the SongLyrics object
        # with a song_lyrics_id value of None (like normal) causes insert to
        # fail with an IntegrityError that states the insert violated the
        # uniqueness constraint on song_lyrics.song_lyrics_id. This despite the
        # INSERT statement displayed in the stack trace clearly not setting
        # song_lyrics_id. Whatever. It's a bug in someone else's code than mine.
        # I work around it by picking the next song_lyrics_id manually, and that
        # seems to work.
        max_song_lyrics_id = max(song_lyrics.song_lyrics_id for song_lyrics in SongLyrics.objects.filter())
        song_lyrics.song_lyrics_id = max_song_lyrics_id + 1
        song_lyrics.song_id = song.song_id
        song_lyrics.save()
        song.song_lyrics_id = song_lyrics.song_lyrics_id
        song.save()
        return JsonResponse(song_lyrics.serialize(), status=status.HTTP_200_OK)

    return dispatch_funcs_by_method((_single_song_lyrics_GET,
                                      _single_song_lyrics_POST), request)


# GET,DELETE        /songs/<song_id>/lyrics/<lyrics_id>
@api_view(['GET', 'DELETE'])
def single_song_single_lyrics(request, outer_model_obj_id, inner_model_obj_id):

    def _single_song_lyrics_GET():
        try:
            Song.objects.get(song_id=outer_model_obj_id)
        except Song.DoesNotExist:
            return JsonResponse({'message': f'no song with song_id={outer_model_obj_id}'},
                                status=status.HTTP_404_NOT_FOUND)
        try:
            song_lyrics = SongLyrics.objects.get(song_lyrics_id=inner_model_obj_id)
        except SongLyrics.DoesNotExist:
            return JsonResponse({'message': f'no song lyrics with song_lyrics_id={inner_model_obj_id}'},
                                status=status.HTTP_404_NOT_FOUND)
        return JsonResponse(song_lyrics.serialize(), status=status.HTTP_200_OK)

    def _single_song_lyrics_DELETE():
        try:
            song = Song.objects.get(song_id=outer_model_obj_id)
        except Song.DoesNotExist:
            return JsonResponse({'message': f'no song with song_id={outer_model_obj_id}'},
                                status=status.HTTP_404_NOT_FOUND)
        try:
            song_lyrics = SongLyrics.objects.get(song_lyrics_id=inner_model_obj_id)
        except SongLyrics.DoesNotExist:
            return JsonResponse({'message': f'no song lyrics with song_lyrics_id={inner_model_obj_id}'},
                                status=status.HTTP_404_NOT_FOUND)
        song.song_lyrics_id = None
        song.save()
        song_lyrics.delete()
        return JsonResponse({'message': f'song lyrics with song_lyrics_id={inner_model_obj_id} '
                                        f'associated with song with song_id={outer_model_obj_id} deleted'},
                            status=status.HTTP_200_OK)

    return dispatch_funcs_by_method((_single_song_lyrics_GET,
                                      _single_song_lyrics_DELETE), request)

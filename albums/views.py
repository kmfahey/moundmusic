#!/usr/bin/python3

from operator import itemgetter

from django.http.response import JsonResponse

from rest_framework import status
from rest_framework.decorators import api_view

from .models import (
    Album,
    AlbumSongBridge,
    Genre,
    AlbumGenreBridge,
    Song,
    Artist,
    ArtistAlbumBridge,
)

from moundmusic.viewutils import (
    index_defclo,
    single_model_defclo,
    outer_id_inner_list_defclo,
    outer_id_inner_id_defclo,
)


# Most of the endpoint functions in this file are closures returned by
# higher-order functions defined in moundmusic.viewutils. See that file
# for the functions that are defining these endpoints.


# GET,POST /albums/
index = index_defclo(Album, "album_id")


# GET,PATCH,DELETE /albums/<album_id>/
single_album = single_model_defclo(Album, "album_id")


# GET /albums/<album_id>/songs
@api_view(["GET"])
def single_album_songs(_, outer_model_obj_id):
    bridge_rows = AlbumSongBridge.objects.filter(album_id=outer_model_obj_id)
    if not len(bridge_rows):
        return JsonResponse(
            {"message": f"no songs with album_id={outer_model_obj_id}"},
            status=status.HTTP_404_NOT_FOUND,
        )
    return_struct = dict()

    # songs are organized by disc number and track number, so it makes
    # sense to structure the output into an object with properties
    # named disc_{number} pointing to objects with properties named
    # track_{number} pointing to the track objects.
    rows_by_disc_and_track_numbers = {
        (bridge_row.disc_number, bridge_row.track_number): bridge_row
        for bridge_row in bridge_rows
    }
    for disc_number in map(itemgetter(0), rows_by_disc_and_track_numbers.keys()):
        return_struct["disc_%i" % disc_number] = dict()
    for (disc_number, track_number), bridge_row in sorted(
        rows_by_disc_and_track_numbers.items()
    ):
        disc_key = "disc_%i" % disc_number
        track_key = "track_%i" % track_number
        return_struct[disc_key][track_key] = Song.objects.get(
            song_id=bridge_row.song_id
        ).serialize()
    return JsonResponse(return_struct, status=status.HTTP_200_OK)


# GET,DELETE /albums/<album_id>/songs/<song_id>
single_album_single_song = outer_id_inner_id_defclo(
    Album, "album_id", Song, "song_id", AlbumSongBridge
)


# GET,POST /albums/<album_id>/genres
single_album_genres = outer_id_inner_list_defclo(
    Album, "album_id", Genre, "genre_id", AlbumGenreBridge
)


# GET,DELETE /albums/<album_id>/genres/<genre_id>
single_album_single_genre = outer_id_inner_id_defclo(
    Album, "album_id", Genre, "genre_id", AlbumGenreBridge
)


# GET,POST /albums/<album_id>/artists/
single_album_artists = outer_id_inner_list_defclo(
    Album, "album_id", Artist, "artist_id", ArtistAlbumBridge
)


# GET,DELETE /albums/<album_id>/artists/<artist_id>/
single_album_single_artist = outer_id_inner_id_defclo(
    Album, "album_id", Artist, "artist_id", ArtistAlbumBridge
)

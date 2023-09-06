#!/usr/bin/python3

from moundmusic.viewutils import (
    index_defclo,
    single_model_defclo,
    outer_id_inner_list_defclo,
    outer_id_inner_id_defclo,
)

from .models import (
    Album,
    Artist,
    Genre,
    Song,
    ArtistAlbumBridge,
    ArtistGenreBridge,
    ArtistSongBridge,
)


# All the endpoint functions in this file are closures returned by
# higher-order functions defined in moundmusic.viewutils. See that file
# for the functions that are defining these endpoints.


# GET,POST /artists
index = index_defclo(Artist, "artist_id")


# GET,PATCH,DELETE /artists/<artist_id>
single_artist = single_model_defclo(Artist, "artist_id")


# GET,POST /artists/<artist_id>/albums
single_artist_albums = outer_id_inner_list_defclo(
    Artist, "artist_id", Album, "album_id", ArtistAlbumBridge
)


# GET,DELETE /artists/<artist_id>/albums/<album_id>
single_artist_single_album = outer_id_inner_id_defclo(
    Artist, "artist_id", Album, "album_id", ArtistAlbumBridge
)


# GET,POST /artists/<artist_id>/songs
single_artist_songs = outer_id_inner_list_defclo(
    Artist, "artist_id", Song, "song_id", ArtistSongBridge
)


# GET,DELETE /artists/<artist_id>/songs/<song_id>
single_artist_single_song = outer_id_inner_id_defclo(
    Artist, "artist_id", Song, "song_id", ArtistSongBridge
)


# GET,POST /artists/<artist_id>/genres
single_artist_genres = outer_id_inner_list_defclo(
    Artist, "artist_id", Genre, "genre_id", ArtistGenreBridge
)


# GET,DELETE /artists/<artist_id>/genres/<genre_id>
single_artist_single_genre = outer_id_inner_id_defclo(
    Artist, "artist_id", Genre, "genre_id", ArtistGenreBridge
)

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
    AlbumGenreBridge,
    ArtistGenreBridge,
    SongGenreBridge,
)


# All the endpoint functions in this file are closures returned by
# higher-order functions defined in moundmusic.viewutils. See that file
# for the functions that are defining these endpoints.


# GET,POST /genres
index = index_defclo(Genre, "genre_id")


# GET,PATCH,DELETE /genres/<genre_id>
single_genre = single_model_defclo(Genre, "genre_id")


# GET,POST /genres/<genre_id>/albums
single_genre_albums = outer_id_inner_list_defclo(
    Genre, "genre_id", Album, "album_id", AlbumGenreBridge
)


# GET,DELETE /genres/<genre_id>/albums/<album_id>
single_genre_single_album = outer_id_inner_id_defclo(
    Genre, "genre_id", Album, "album_id", AlbumGenreBridge
)


# GET,POST /genres/<genre_id>/artists
single_genre_artists = outer_id_inner_list_defclo(
    Genre, "genre_id", Artist, "artist_id", ArtistGenreBridge
)


# GET,DELETE /genres/<genre_id>/artists/<artist_id>
single_genre_single_artist = outer_id_inner_id_defclo(
    Genre, "genre_id", Artist, "artist_id", ArtistGenreBridge
)


# GET,POST /genres/<genre_id>/songs
single_genre_songs = outer_id_inner_list_defclo(
    Genre, "genre_id", Song, "song_id", SongGenreBridge
)


# GET,DELETE /genres/<genre_id>/songs/<song_id>
single_genre_single_song = outer_id_inner_id_defclo(
    Genre, "genre_id", Song, "song_id", SongGenreBridge
)

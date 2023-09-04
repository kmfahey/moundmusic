#!/usr/bin/python3

from moundmusic.viewutils import (
    define_GET_POST_index_closure,
    define_single_model_GET_PATCH_DELETE_closure,
    define_single_outer_model_all_of_inner_model_GET_POST_closure,
    define_single_outer_model_single_inner_model_GET_DELETE_closure,
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
index = define_GET_POST_index_closure(Genre, "genre_id")


# GET,PATCH,DELETE /genres/<genre_id>
single_genre = define_single_model_GET_PATCH_DELETE_closure(Genre, "genre_id")


# GET,POST /genres/<genre_id>/albums
single_genre_albums = define_single_outer_model_all_of_inner_model_GET_POST_closure(
    Genre, "genre_id", Album, "album_id", AlbumGenreBridge
)


# GET,DELETE /genres/<genre_id>/albums/<album_id>
single_genre_single_album = (
    define_single_outer_model_single_inner_model_GET_DELETE_closure(
        Genre, "genre_id", Album, "album_id", AlbumGenreBridge
    )
)


# GET,POST /genres/<genre_id>/artists
single_genre_artists = define_single_outer_model_all_of_inner_model_GET_POST_closure(
    Genre, "genre_id", Artist, "artist_id", ArtistGenreBridge
)


# GET,DELETE /genres/<genre_id>/artists/<artist_id>
single_genre_single_artist = (
    define_single_outer_model_single_inner_model_GET_DELETE_closure(
        Genre, "genre_id", Artist, "artist_id", ArtistGenreBridge
    )
)


# GET,POST /genres/<genre_id>/songs
single_genre_songs = define_single_outer_model_all_of_inner_model_GET_POST_closure(
    Genre, "genre_id", Song, "song_id", SongGenreBridge
)


# GET,DELETE /genres/<genre_id>/songs/<song_id>
single_genre_single_song = (
    define_single_outer_model_single_inner_model_GET_DELETE_closure(
        Genre, "genre_id", Song, "song_id", SongGenreBridge
    )
)

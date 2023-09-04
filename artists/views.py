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
    ArtistAlbumBridge,
    ArtistGenreBridge,
    ArtistSongBridge,
)


# All the endpoint functions in this file are closures returned by
# higher-order functions defined in moundmusic.viewutils. See that file
# for the functions that are defining these endpoints.


# GET,POST /artists
index = define_GET_POST_index_closure(Artist, "artist_id")


# GET,PATCH,DELETE /artists/<artist_id>
single_artist = define_single_model_GET_PATCH_DELETE_closure(Artist, "artist_id")


# GET,POST /artists/<artist_id>/albums
single_artist_albums = define_single_outer_model_all_of_inner_model_GET_POST_closure(
    Artist, "artist_id", Album, "album_id", ArtistAlbumBridge
)


# GET,DELETE /artists/<artist_id>/albums/<album_id>
single_artist_single_album = (
    define_single_outer_model_single_inner_model_GET_DELETE_closure(
        Artist, "artist_id", Album, "album_id", ArtistAlbumBridge
    )
)


# GET,POST /artists/<artist_id>/songs
single_artist_songs = define_single_outer_model_all_of_inner_model_GET_POST_closure(
    Artist, "artist_id", Song, "song_id", ArtistSongBridge
)


# GET,DELETE /artists/<artist_id>/songs/<song_id>
single_artist_single_song = (
    define_single_outer_model_single_inner_model_GET_DELETE_closure(
        Artist, "artist_id", Song, "song_id", ArtistSongBridge
    )
)


# GET,POST /artists/<artist_id>/genres
single_artist_genres = define_single_outer_model_all_of_inner_model_GET_POST_closure(
    Artist, "artist_id", Genre, "genre_id", ArtistGenreBridge
)


# GET,DELETE /artists/<artist_id>/genres/<genre_id>
single_artist_single_genre = (
    define_single_outer_model_single_inner_model_GET_DELETE_closure(
        Artist, "artist_id", Genre, "genre_id", ArtistGenreBridge
    )
)

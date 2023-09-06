#!/usr/bin/python3

from moundmusic.viewutils import (
    index_defclo,
    single_model_defclo,
    one_outer_all_inner_defclo,
    single_single_defclo,
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
single_artist_albums = one_outer_all_inner_defclo(
    Artist, "artist_id", Album, "album_id", ArtistAlbumBridge
)


# GET,DELETE /artists/<artist_id>/albums/<album_id>
single_artist_single_album = single_single_defclo(
    Artist, "artist_id", Album, "album_id", ArtistAlbumBridge
)


# GET,POST /artists/<artist_id>/songs
single_artist_songs = one_outer_all_inner_defclo(
    Artist, "artist_id", Song, "song_id", ArtistSongBridge
)


# GET,DELETE /artists/<artist_id>/songs/<song_id>
single_artist_single_song = single_single_defclo(
    Artist, "artist_id", Song, "song_id", ArtistSongBridge
)


# GET,POST /artists/<artist_id>/genres
single_artist_genres = one_outer_all_inner_defclo(
    Artist, "artist_id", Genre, "genre_id", ArtistGenreBridge
)


# GET,DELETE /artists/<artist_id>/genres/<genre_id>
single_artist_single_genre = single_single_defclo(
    Artist, "artist_id", Genre, "genre_id", ArtistGenreBridge
)

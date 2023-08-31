#!/usr/bin/python3

import pytest
import re
import random
import json

from django.test.client import RequestFactory
from django.http.response import JsonResponse

from .models import Album, Song, SongLyrics, AlbumSongBridge

from .views import (
    single_song_albums,
    single_song_single_album,
    single_song_lyrics,
    single_song_single_lyrics,
)

request_factory = RequestFactory()

matches_date_isoformat = lambda strval: bool(re.match(r"^\d{4}-\d{2}-\d{2}$", strval))


@pytest.mark.django_db
def test_single_song_albums_GET():
    songs = Song.objects.filter()
    song = random.choice(songs)
    song_id = song.song_id
    request = request_factory.get(f"/songs/{song_id}/albums")
    response = single_song_albums(request, song_id)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert len(json_content)
    sample_object = random.choice(json_content)
    assert "disc_number" in sample_object and isinstance(
        sample_object["disc_number"], int
    )
    assert "track_number" in sample_object and isinstance(
        sample_object["track_number"], int
    )
    album_object = sample_object["album"]
    assert "album_id" in album_object and isinstance(album_object["album_id"], int)
    assert "title" in album_object and isinstance(album_object["title"], str)
    assert "number_of_tracks" in album_object and isinstance(
        album_object["number_of_tracks"], int
    )
    assert "number_of_discs" in album_object and isinstance(
        album_object["number_of_discs"], int
    )
    assert (
        "release_date" in album_object
        and isinstance(album_object["release_date"], str)
        and matches_date_isoformat(album_object["release_date"])
    )


@pytest.mark.django_db
def test_single_song_albums_GET_error_nonexistent_song_id():
    songs = Song.objects.filter()
    song_ids = [song.song_id for song in songs]
    while True:
        song_id = random.randint(1, 9999)
        if song_id not in song_ids:
            break
    request = request_factory.get(f"/songs/{song_id}/albums")
    response = single_song_albums(request, song_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content
    assert json_content["message"] == f"no song with song_id={song_id}"


@pytest.mark.django_db
def test_single_song_single_album_GET():
    songs = Song.objects.filter()
    song = random.choice(songs)
    song_id = song.song_id
    bridge_rows = AlbumSongBridge.objects.filter(song_id=song_id)
    bridge_row = random.choice(bridge_rows)
    album = Album.objects.get(album_id=bridge_row.album_id)
    album_id = album.album_id
    request = request_factory.get(f"/songs/{song_id}/albums/{album_id}")
    response = single_song_single_album(request, song_id, album_id)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert len(json_content)
    assert "disc_number" in json_content and isinstance(
        json_content["disc_number"], int
    )
    assert "track_number" in json_content and isinstance(
        json_content["track_number"], int
    )
    album_object = json_content["album"]
    assert "album_id" in album_object and isinstance(album_object["album_id"], int)
    assert "title" in album_object and isinstance(album_object["title"], str)
    assert "number_of_tracks" in album_object and isinstance(
        album_object["number_of_tracks"], int
    )
    assert "number_of_discs" in album_object and isinstance(
        album_object["number_of_discs"], int
    )
    assert (
        "release_date" in album_object
        and isinstance(album_object["release_date"], str)
        and matches_date_isoformat(album_object["release_date"])
    )


@pytest.mark.django_db
def test_single_song_single_album_GET_error_nonexistent_song_id():
    song_ids = [song.song_id for song in Song.objects.filter()]
    while True:
        song_id = random.randint(1, 9999)
        if song_id not in song_ids:
            break
    album_ids = [album.album_id for album in Album.objects.filter()]
    while True:
        album_id = random.randint(1, 9999)
        if album_id not in album_ids:
            break
    request = request_factory.get(f"/songs/{song_id}/albums/{album_id}")
    response = single_song_single_album(request, song_id, album_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content
    assert json_content["message"] == f"no song with song_id={song_id}"


@pytest.mark.django_db
def test_single_song_lyrics_GET():
    songs = Song.objects.filter()
    song = random.choice(songs)
    song_id = song.song_id
    request = request_factory.get(f"/songs/{song_id}/lyrics")
    response = single_song_lyrics(request, song_id)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert len(json_content)
    assert "song_id" in json_content and isinstance(json_content["song_id"], int)
    assert "song_lyrics_id" in json_content and isinstance(
        json_content["song_lyrics_id"], int
    )
    assert "lyrics" in json_content and isinstance(json_content["lyrics"], str)


@pytest.mark.django_db
def test_single_song_lyrics_GET_error_nonexistent_song_id():
    songs = Song.objects.filter()
    song_ids = [song.song_id for song in songs]
    while True:
        song_id = random.randint(1, 9999)
        if song_id not in song_ids:
            break
    request = request_factory.get(f"/songs/{song_id}/lyrics")
    response = single_song_lyrics(request, song_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content
    assert json_content["message"] == f"no song with song_id={song_id}"


@pytest.mark.django_db
def test_single_song_lyrics_GET_error_nonexistent_song_lyrics_id():
    songs = Song.objects.filter()
    song = random.choice(songs)
    song_id, song_lyrics_id = song.song_id, song.song_lyrics_id
    song_lyrics = SongLyrics.objects.get(song_lyrics_id=song_lyrics_id)
    song.song_lyrics_id = None
    song.save()
    song_lyrics.delete()
    request = request_factory.get(f"/songs/{song_id}/lyrics")
    response = single_song_lyrics(request, song_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content
    assert (
        json_content["message"]
        == f"no song lyrics associated with song with song_id={song_id}"
    )


@pytest.mark.django_db
def test_single_song_song_lyrics_POST():
    songs = Song.objects.filter()
    song = random.choice(songs)
    song_id = song.song_id
    song.song_lyrics_id = None
    song.save()
    lyrics = "A man, a plan, a canal: Panama!"
    request = request_factory.post(
        f"/songs/{song_id}/lyrics",
        data={"lyrics": lyrics},
        content_type="application/json",
    )
    response = single_song_lyrics(request, song_id)
    assert response.status_code == 200
    json_content = json.loads(response.content)
    assert "lyrics" in json_content and json_content["lyrics"] == lyrics
    assert "song_id" in json_content and json_content["song_id"] == song_id
    assert "song_lyrics_id" in json_content and isinstance(
        json_content["song_lyrics_id"], int
    )


@pytest.mark.django_db
def test_single_song_song_lyrics_POST_error_nonexistent_song_id():
    song_ids = [song.song_id for song in Song.objects.filter()]
    while True:
        song_id = random.randint(1, 9999)
        if song_id not in song_ids:
            break
    song_lyrics_ids = [
        song_lyrics.song_lyrics_id for song_lyrics in SongLyrics.objects.filter()
    ]
    song_lyrics_id = random.choice(song_lyrics_ids)
    new_song_lyrics_assoc_dict = {"song_lyrics_id": song_lyrics_id}
    request = request_factory.post(
        f"/songs/{song_id}/song_lyrics",
        data=new_song_lyrics_assoc_dict,
        content_type="application/json",
    )
    response = single_song_lyrics(request, song_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content
    assert json_content["message"] == f"no song with song_id={song_id}"


@pytest.mark.django_db
def test_single_song_song_lyrics_POST_song_already_has_song_lyrics_associated():
    songs = Song.objects.filter()
    song = random.choice(songs)
    song_id = song.song_id
    lyrics = "A man, a plan, a canal: Panama!"
    request = request_factory.post(
        f"/songs/{song_id}/lyrics",
        data={"lyrics": lyrics},
        content_type="application/json",
    )
    response = single_song_lyrics(request, song_id)
    assert response.status_code == 409
    json_content = json.loads(response.content)
    assert "message" in json_content
    assert (
        json_content["message"]
        == f"song with song_id={song_id} already has song lyrics with "
        f"song_lyrics_id={song.song_lyrics_id} associated with it"
    )


@pytest.mark.django_db
def test_single_song_single_song_lyrics_GET():
    songs = Song.objects.filter()
    song = random.choice(songs)
    song_id, song_lyrics_id = song.song_id, song.song_lyrics_id
    request = request_factory.get(f"/songs/{song_id}/song_lyrics/{song_lyrics_id}")
    response = single_song_single_lyrics(request, song_id, song_lyrics_id)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert len(json_content)
    assert "song_id" in json_content and json_content["song_id"] == song_id
    assert (
        "song_lyrics_id" in json_content
        and json_content["song_lyrics_id"] == song_lyrics_id
    )
    assert "lyrics" in json_content and isinstance(json_content["lyrics"], str)


@pytest.mark.django_db
def test_single_song_single_lyrics_GET_error_nonexistent_song_id():
    song_ids = [song.song_id for song in Song.objects.filter()]
    while True:
        song_id = random.randint(1, 9999)
        if song_id not in song_ids:
            break
    song_lyrics_objs = SongLyrics.objects.filter()
    song_lyrics = random.choice(song_lyrics_objs)
    song_lyrics_id = song_lyrics.song_lyrics_id
    request = request_factory.get(f"/songs/{song_id}/lyrics/{song_lyrics_id}")
    response = single_song_single_lyrics(request, song_id, song_lyrics_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content
    assert json_content["message"] == f"no song with song_id={song_id}"


@pytest.mark.django_db
def test_single_song_single_lyrics_GET_error_nonexistent_song_lyrics_id():
    songs = Song.objects.filter()
    song = random.choice(songs)
    song_id = song.song_id
    song_lyrics_ids = [
        song_lyrics.song_lyrics_id for song_lyrics in SongLyrics.objects.filter()
    ]
    while True:
        song_lyrics_id = random.randint(1, 9999)
        if song_lyrics_id not in song_lyrics_ids:
            break
    request = request_factory.get(f"/songs/{song_id}/lyrics/{song_lyrics_id}")
    response = single_song_single_lyrics(request, song_id, song_lyrics_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content
    assert (
        json_content["message"]
        == f"no song lyrics with song_lyrics_id={song_lyrics_id}"
    )


@pytest.mark.django_db
def test_single_song_single_song_lyrics_DELETE():
    songs = Song.objects.filter()
    song = random.choice(songs)
    song_id, song_lyrics_id = song.song_id, song.song_lyrics_id
    request = request_factory.delete(f"/songs/{song_id}/song_lyrics/{song_lyrics_id}")
    response = single_song_single_lyrics(request, song_id, song_lyrics_id)
    assert response.status_code == 200
    json_content = json.loads(response.content)
    assert "message" in json_content
    assert json_content["message"] == (
        f"song lyrics with song_lyrics_id={song_lyrics_id} "
        f"associated with song with song_id={song_id} deleted"
    )
    try:
        SongLyrics.objects.get(song_lyrics_id=song_lyrics_id)
        pytest.fail()
    except SongLyrics.DoesNotExist as exception:
        assert isinstance(exception, SongLyrics.DoesNotExist)


@pytest.mark.django_db
def test_single_song_single_song_lyrics_DELETE_error_nonexistent_song_id():
    song_ids = [song.song_id for song in Song.objects.filter()]
    while True:
        song_id = random.randint(1, 9999)
        if song_id not in song_ids:
            break
    song_lyrics_objs = SongLyrics.objects.filter()
    song_lyrics = random.choice(song_lyrics_objs)
    song_lyrics_id = song_lyrics.song_lyrics_id
    request = request_factory.delete(f"/songs/{song_id}/song_lyrics/{song_lyrics_id}")
    response = single_song_single_lyrics(request, song_id, song_lyrics_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content
    assert json_content["message"] == f"no song with song_id={song_id}"


@pytest.mark.django_db
def test_single_song_single_song_lyrics_DELETE_error_nonexistent_song_lyrics_id():
    song_objs = Song.objects.filter()
    song = random.choice(song_objs)
    song_id = song.song_id
    song_lyrics_ids = [
        song_lyrics.song_lyrics_id for song_lyrics in SongLyrics.objects.filter()
    ]
    while True:
        song_lyrics_id = random.randint(1, 9999)
        if song_lyrics_id not in song_lyrics_ids:
            break
    request = request_factory.delete(f"/songs/{song_id}/song_lyrics/{song_lyrics_id}")
    response = single_song_single_lyrics(request, song_id, song_lyrics_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content
    assert (
        json_content["message"]
        == f"no song lyrics with song_lyrics_id={song_lyrics_id}"
    )

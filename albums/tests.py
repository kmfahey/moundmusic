#!/usr/bin/python3

import pytest
import re
import random

from datetime import date

from json import loads as json_loads
from json import dumps as json_dumps

from django.test.client import RequestFactory
from django.http.response import JsonResponse

from .models import Album, Song, AlbumSongBridge, AlbumGenreBridge, Genre
from .views import index, single_album, single_album_songs, single_album_single_song, single_album_genres, \
        single_album_single_genre

request_factory = RequestFactory()

matches_date_isoformat = lambda strval: bool(re.match(r"^\d{4}-\d{2}-\d{2}$", strval))


@pytest.mark.django_db
def test_index_GET():
    request = request_factory.get("/albums/")
    response = index(request)
    assert isinstance(response, JsonResponse)
    json_content = json_loads(response.content)
    assert len(json_content)
    assert isinstance(json_content, list)
    sample_album_jsobject = json_content[0]
    assert "album_id" in sample_album_jsobject and         isinstance(sample_album_jsobject.get("album_id"), int)
    assert "title" in sample_album_jsobject and            isinstance(sample_album_jsobject.get("title"), str)
    assert "number_of_discs" in sample_album_jsobject and  isinstance(sample_album_jsobject.get("number_of_discs"), int)
    assert "number_of_tracks" in sample_album_jsobject and isinstance(sample_album_jsobject.get("number_of_tracks"), int)
    assert "release_date" in sample_album_jsobject and     isinstance(sample_album_jsobject.get("release_date"), str)
    assert matches_date_isoformat(sample_album_jsobject["release_date"])
    assert "album_cover_id" in sample_album_jsobject and   isinstance(sample_album_jsobject.get("album_cover_id"), int)


@pytest.mark.django_db
def test_index_POST():
    new_album_dict = {
        "title": "Some Album",
        "number_of_discs": 1,
        "number_of_tracks": 12,
        "release_date": "1998-01-01"
    }
    request = request_factory.post("/albums/", data=new_album_dict, content_type="application/json")
    response = index(request)
    assert isinstance(response, JsonResponse)
    json_content = json_loads(response.content)
    assert len(json_content)
    assert isinstance(json_content, dict)
    try:
        new_test_album = Album.objects.get(album_id=json_content["album_id"])
    except (KeyError, Album.DoesNotExist):
        pytest.fail()
    assert new_test_album.title                    == new_album_dict["title"]
    assert new_test_album.number_of_discs          == new_album_dict["number_of_discs"]
    assert new_test_album.number_of_tracks         == new_album_dict["number_of_tracks"]
    assert new_test_album.release_date.isoformat() == new_album_dict["release_date"]


@pytest.mark.django_db
def test_index_POST_error_invalid_args():
    new_album_dict = {
        "title": "",
        "number_of_discs": 1,
        "number_of_tracks": 12,
        "release_date": "1998-01-01"
    }
    request = request_factory.post("/albums/", data=new_album_dict, content_type="application/json")
    response = index(request)
    assert response.status_code == 400
    assert isinstance(response, JsonResponse)
    json_content = json_loads(response.content)
    assert len(json_content)
    assert isinstance(json_content, dict)
    assert json_content['message'] == "value for 'title' is a string of zero length"



@pytest.mark.django_db
def test_single_album_GET():
    new_album_dict = {
        "title": "Some Album",
        "number_of_discs": 1,
        "number_of_tracks": 12,
        "release_date": "1998-01-01"
    }
    album = Album(**new_album_dict)
    album.save()
    album_id = album.album_id
    request = request_factory.get(f"/albums/{album_id}")
    response = single_album(request, album_id)
    json_content = json_loads(response.content)
    assert json_content["title"]            == album.title
    assert json_content["number_of_discs"]  == album.number_of_discs
    assert json_content["number_of_tracks"] == album.number_of_tracks
    assert json_content["release_date"]     == album.release_date
    assert matches_date_isoformat(json_content["release_date"])
    assert json_content["album_id"]         == album.album_id
    assert json_content["album_cover_id"]   is None


@pytest.mark.django_db
def test_single_album_GET_error_nonexistent_album_id():
    albums = Album.objects.filter()
    album_ids = [album.album_id for album in albums]
    while True:
        album_id = random.randint(1,9999)
        if album_id not in album_ids:
            break
    request = request_factory.get(f"/albums/{album_id}")
    response = single_album(request, album_id)
    assert response.status_code == 404
    json_content = json_loads(response.content)
    assert "message" in json_content and json_content["message"] == f'no album with album_id={album_id}'


@pytest.mark.django_db
def test_single_album_PATCH():
    new_album_dict = {
        "title": "Some Album",
        "number_of_discs": 1,
        "number_of_tracks": 12,
        "release_date": "1998-01-01"
    }
    album = Album(**new_album_dict)
    album.save()
    album_id = album.album_id
    album_patch_dict = {"title": "Some Other Album"}
    request = request_factory.patch(f"/albums/{album_id}", data=album_patch_dict, content_type="application/json")
    response = single_album(request, album_id)
    json_content = json_loads(response.content)
    album = Album.objects.get(album_id=album_id)
    assert json_content["title"]            == "Some Other Album"
    assert json_content["number_of_discs"]  == new_album_dict["number_of_discs"]
    assert json_content["number_of_tracks"] == new_album_dict["number_of_tracks"]
    assert json_content["release_date"]     == new_album_dict["release_date"]
    assert album.title                    == "Some Other Album"
    assert album.number_of_discs          == new_album_dict["number_of_discs"]
    assert album.number_of_tracks         == new_album_dict["number_of_tracks"]
    assert album.release_date.isoformat() == new_album_dict["release_date"]


@pytest.mark.django_db
def test_single_album_PATCH_error_nonexistent_album_id():
    album_patch_dict = {"title":"Foo"}
    albums = Album.objects.filter()
    album_ids = [album.album_id for album in albums]
    while True:
        album_id = random.randint(1,9999)
        if album_id not in album_ids:
            break
    request = request_factory.patch(f"/albums/{album_id}", data=album_patch_dict, content_type="application/json")
    response = single_album(request, album_id)
    assert response.status_code == 404
    json_content = json_loads(response.content)
    assert "message" in json_content and json_content["message"] == f'no album with album_id={album_id}'


@pytest.mark.django_db
def test_single_album_PATCH_error_invalid_args():
    album_patch_dict = { "title": "" }
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    request = request_factory.patch(f"/albums/{album_id}", data=album_patch_dict, content_type="application/json")
    response = single_album(request, album_id)
    assert response.status_code == 400
    assert isinstance(response, JsonResponse)
    json_content = json_loads(response.content)
    assert len(json_content)
    assert isinstance(json_content, dict)
    assert json_content['message'] == "value for 'title' is a string of zero length"


@pytest.mark.django_db
def test_single_album_DELETE():
    album = Album.objects.filter()[0]
    album_id = album.album_id
    request = request_factory.delete(f"/albums/{album_id}")
    response = single_album(request, album_id)
    json_content = json_loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f'album with album_id={album_id} deleted'
    try:
        Album.objects.get(album_id=album_id)
        pytest.fail()
    except Album.DoesNotExist as exception:
        assert isinstance(exception, Album.DoesNotExist)


@pytest.mark.django_db
def test_single_album_DELETE_error_nonexistent_album_id():
    albums = Album.objects.filter()
    album_ids = [album.album_id for album in albums]
    while True:
        album_id = random.randint(1,9999)
        if album_id not in album_ids:
            break
    request = request_factory.delete(f"/albums/{album_id}")
    response = single_album(request, album_id)
    assert response.status_code == 404
    json_content = json_loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f'no album with album_id={album_id}'


@pytest.mark.django_db
def test_single_album_songs_GET():
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    request = request_factory.get(f"/albums/{album_id}/songs")
    response = single_album_songs(request, album_id)
    assert isinstance(response, JsonResponse)
    json_content = json_loads(response.content)
    assert len(json_content)
    assert "disc_1" in json_content
    disc_dict = json_content["disc_1"]
    assert "track_1" in disc_dict
    track_dict = disc_dict["track_1"]
    assert 'song_id' in track_dict and isinstance(track_dict['song_id'], int)
    assert 'title' in track_dict and isinstance(track_dict['title'], str)
    assert 'length_minutes' in track_dict and isinstance(track_dict['length_minutes'], int)
    assert 'length_seconds' in track_dict and isinstance(track_dict['length_seconds'], int)
    assert 'song_lyrics_id' in track_dict and isinstance(track_dict['song_lyrics_id'], int)


@pytest.mark.django_db
def test_single_album_songs_GET_error_nonexistent_album_id():
    albums = Album.objects.filter()
    album_ids = [album.album_id for album in albums]
    while True:
        album_id = random.randint(1,9999)
        if album_id not in album_ids:
            break
    request = request_factory.get(f"/albums/{album_id}/songs")
    response = single_album_songs(request, album_id)
    assert response.status_code == 404
    json_content = json_loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f'no songs with album_id={album_id}'


@pytest.mark.django_db
def test_single_album_single_song_GET():
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    bridge_rows = AlbumSongBridge.objects.filter(album_id=album_id)
    bridge_row = random.choice(bridge_rows)
    song = Song.objects.get(song_id=bridge_row.song_id)
    song_id = song.song_id
    request = request_factory.get(f"/albums/{album_id}/songs/{song_id}")
    response = single_album_single_song(request, album_id, song_id)
    assert isinstance(response, JsonResponse)
    json_content = json_loads(response.content)
    assert len(json_content)
    assert 'song_id' in json_content and json_content['song_id'] == song_id
    assert 'title' in json_content and isinstance(json_content['title'], str)
    assert 'length_minutes' in json_content and isinstance(json_content['length_minutes'], int)
    assert 'length_seconds' in json_content and isinstance(json_content['length_seconds'], int)
    assert 'song_lyrics_id' in json_content and isinstance(json_content['song_lyrics_id'], int)


@pytest.mark.django_db
def test_single_album_single_song_GET():
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    bridge_rows = AlbumSongBridge.objects.filter(album_id=album_id)
    bridge_row = random.choice(bridge_rows)
    song = Song.objects.get(song_id=bridge_row.song_id)
    song_id = song.song_id
    request = request_factory.get(f"/albums/{album_id}/songs/{song_id}")
    response = single_album_single_song(request, album_id, song_id)
    assert isinstance(response, JsonResponse)
    json_content = json_loads(response.content)
    assert len(json_content)
    assert 'song_id' in json_content and json_content['song_id'] == song_id
    assert 'title' in json_content and isinstance(json_content['title'], str)
    assert 'length_minutes' in json_content and isinstance(json_content['length_minutes'], int)
    assert 'length_seconds' in json_content and isinstance(json_content['length_seconds'], int)
    assert 'song_lyrics_id' in json_content and isinstance(json_content['song_lyrics_id'], int)


@pytest.mark.django_db
def test_single_album_single_song_GET_error_nonexistent_album_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    while True:
        album_id = random.randint(1,9999)
        if album_id not in album_ids:
            break
    song_ids = [song.song_id for song in Song.objects.filter()]
    while True:
        song_id = random.randint(1,9999)
        if song_id not in song_ids:
            break
    request = request_factory.get(f"/albums/{album_id}/songs/{song_id}")
    response = single_album_single_song(request, album_id, song_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json_loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f'no album with album_id={album_id}'


@pytest.mark.django_db
def test_single_album_single_song_PATCH():
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    bridge_rows = AlbumSongBridge.objects.filter(album_id=album_id)
    bridge_row = random.choice(bridge_rows)
    song = Song.objects.get(song_id=bridge_row.song_id)
    song_id = song.song_id
    song_patch_dict = {"title":''.join(reversed(song.title))}
    request = request_factory.patch(f"/albums/{album_id}/songs/{song_id}", data=song_patch_dict, content_type="application/json")
    response = single_album_single_song(request, album_id, song_id)
    json_content = json_loads(response.content)
    assert 'song_id' in json_content and json_content['song_id'] == song_id
    assert 'title' in json_content and json_content['title'] == song_patch_dict["title"]
    assert 'length_minutes' in json_content and json_content['length_minutes'] == song.length_minutes
    assert 'length_seconds' in json_content and json_content['length_seconds'] == song.length_seconds
    assert 'song_lyrics_id' in json_content and json_content['song_lyrics_id'] == song.song_lyrics_id


@pytest.mark.django_db
def test_single_album_single_song_PATCH_error_nonexistent_song_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    album_id = random.choice(album_ids)
    song_ids = [song.song_id for song in Song.objects.filter()]
    while True:
        song_id = random.randint(1,9999)
        if song_id not in song_ids:
            break
    song_patch_dict = {"title":"Foo"}
    request = request_factory.patch(f"/albums/{album_id}/songs/{song_id}", data=song_patch_dict, content_type="application/json")
    response = single_album_single_song(request, album_id, song_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json_loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f'album with album_id={album_id} has no song with song_id={song_id}'


@pytest.mark.django_db
def test_single_album_single_song_PATCH_error_invalid_args():
    album_ids = [album.album_id for album in Album.objects.filter()]
    album_id = random.choice(album_ids)
    bridge_rows = AlbumSongBridge.objects.filter(album_id=album_id)
    song_ids = [bridge_row.song_id for bridge_row in bridge_rows]
    song_id = random.choice(song_ids)
    song_patch_dict = {"length_minutes":-1}
    request = request_factory.patch(f"/albums/{album_id}/songs/{song_id}", data=song_patch_dict, content_type="application/json")
    response = single_album_single_song(request, album_id, song_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 400
    json_content = json_loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f"value for 'length_minutes' isn't greater than 0: -1"


@pytest.mark.django_db
def test_single_album_single_song_DELETE():
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    bridge_rows = AlbumSongBridge.objects.filter(album_id=album_id)
    bridge_row = random.choice(bridge_rows)
    song = Song.objects.get(song_id=bridge_row.song_id)
    song_id = song.song_id
    request = request_factory.delete(f"/albums/{album_id}/songs/{song_id}")
    response = single_album_single_song(request, album_id, song_id)
    json_content = json_loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f'song with album_id={album_id} and song_id={song_id} deleted'
    try:
        Song.objects.get(song_id=song_id)
        pytest.fail()
    except Song.DoesNotExist as exception:
        assert isinstance(exception, Song.DoesNotExist)


@pytest.mark.django_db
def test_single_album_single_song_DELETE_error_nonexistent_album_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    while True:
        album_id = random.randint(1,9999)
        if album_id not in album_ids:
            break
    song_ids = [song.song_id for song in Song.objects.filter()]
    while True:
        song_id = random.randint(1,9999)
        if song_id not in song_ids:
            break
    request = request_factory.delete(f"/albums/{album_id}/songs/{song_id}")
    response = single_album_single_song(request, album_id, song_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json_loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f"no album with album_id={album_id}"


@pytest.mark.django_db
def test_single_album_single_song_DELETE_error_nonexistent_song_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    album_id = random.choice(album_ids)
    song_ids = [song.song_id for song in Song.objects.filter()]
    while True:
        song_id = random.randint(1,9999)
        if song_id not in song_ids:
            break
    request = request_factory.delete(f"/albums/{album_id}/songs/{song_id}")
    response = single_album_single_song(request, album_id, song_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json_loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f"album with album_id={album_id} has no song with song_id={song_id}"


@pytest.mark.django_db
def test_single_album_genres_GET():
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    request = request_factory.get(f"/albums/{album_id}/genres")
    response = single_album_genres(request, album_id)
    assert isinstance(response, JsonResponse)
    json_content = json_loads(response.content)
    assert len(json_content)
    genre_dict = random.choice(json_content)
    assert 'genre_id' in genre_dict and isinstance(genre_dict['genre_id'], int)
    assert 'genre_name' in genre_dict and isinstance(genre_dict['genre_name'], str)


@pytest.mark.django_db
def test_single_album_genres_GET_error_nonexistent_album_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    while True:
        album_id = random.randint(1,9999)
        if album_id not in album_ids:
            break
    request = request_factory.get(f"/albums/{album_id}/genres")
    response = single_album_genres(request, album_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json_loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f"no album with album_id={album_id}"


@pytest.mark.django_db
def test_single_album_genres_POST():
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    bridge_rows = AlbumGenreBridge.objects.filter(album_id=album_id)
    album_already_in_genre_ids = [bridge_row.genre_id for bridge_row in bridge_rows]
    while True:
        genre = random.choice(Genre.objects.filter())
        genre_id = genre.genre_id
        if genre_id not in album_already_in_genre_ids:
            break
    new_genre_assoc_dict = { "genre_id": genre_id }
    request = request_factory.post(f"/albums/{album_id}/genres", data=new_genre_assoc_dict, content_type="application/json")
    response = single_album_genres(request, album_id)
    assert isinstance(response, JsonResponse)
    json_content = json_loads(response.content)
    assert len(json_content)
    assert isinstance(json_content, dict)
    assert json_content["genre_id"] == genre_id
    assert json_content["genre_name"] == genre.genre_name
    bridge_rows = AlbumGenreBridge.objects.filter(album_id=album_id)
    assert any(bridge_row.genre_id == genre_id for bridge_row in bridge_rows)


@pytest.mark.django_db
def test_single_album_genres_POST_error_nonexistent_album_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    while True:
        album_id = random.randint(1,9999)
        if album_id not in album_ids:
            break
    genre_ids = [genre.genre_id for genre in Genre.objects.filter()]
    genre_id = random.choice(genre_ids)
    new_genre_assoc_dict = { "genre_id": genre_id }
    request = request_factory.post(f"/albums/{album_id}/genres", data=new_genre_assoc_dict, content_type="application/json")
    response = single_album_genres(request, album_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json_loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f"no album with album_id={album_id}"


@pytest.mark.django_db
def test_single_album_genres_POST_error_nonexistent_genre_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    album_id = random.choice(album_ids)
    genre_ids = [genre.genre_id for genre in Genre.objects.filter()]
    while True:
        genre_id = random.randint(1,99)
        if genre_id not in genre_ids:
            break
    new_genre_assoc_dict = { "genre_id": genre_id }
    request = request_factory.post(f"/albums/{album_id}/genres", data=new_genre_assoc_dict, content_type="application/json")
    response = single_album_genres(request, album_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json_loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f"no genre with genre_id={genre_id}"


@pytest.mark.django_db
def test_single_album_genres_POST_error_invalid_args():
    album_ids = [album.album_id for album in Album.objects.filter()]
    album_id = random.choice(album_ids)
    genre_ids = [genre.genre_id for genre in Genre.objects.filter()]
    genre_id = random.choice(genre_ids)
    new_genre_assoc_dict = { "genre_id": genre_id, "foo":"bar" }
    request = request_factory.post(f"/albums/{album_id}/genres", data=new_genre_assoc_dict, content_type="application/json")
    response = single_album_genres(request, album_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 400
    json_content = json_loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f"unexpected property: 'foo'"


@pytest.mark.django_db
def test_single_album_single_genre_GET():
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    bridge_rows = AlbumGenreBridge.objects.filter(album_id=album_id)
    bridge_row = random.choice(bridge_rows)
    genre = Genre.objects.get(genre_id=bridge_row.genre_id)
    genre_id = genre.genre_id
    request = request_factory.get(f"/albums/{album_id}/genres/{genre_id}")
    response = single_album_single_genre(request, album_id, genre_id)
    assert isinstance(response, JsonResponse)
    json_content = json_loads(response.content)
    assert len(json_content)
    assert 'genre_id' in json_content and json_content['genre_id'] == genre_id
    assert 'genre_name' in json_content and isinstance(json_content['genre_name'], str)


@pytest.mark.django_db
def test_single_album_single_genre_GET_error_nonexistent_album_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    while True:
        album_id = random.randint(1,9999)
        if album_id not in album_ids:
            break
    genre_ids = [genre.genre_id for genre in Genre.objects.filter()]
    genre_id = random.choice(genre_ids)
    request = request_factory.get(f"/albums/{album_id}/genres/{genre_id}")
    response = single_album_single_genre(request, album_id, genre_id)
    assert response.status_code == 404
    json_content = json_loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f"no album with album_id={album_id}"


@pytest.mark.django_db
def test_single_album_single_genre_GET_error_nonexistent_genre_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    album_id = random.choice(album_ids)
    genre_ids = [genre.genre_id for genre in Genre.objects.filter()]
    while True:
        genre_id = random.randint(1,99)
        if genre_id not in genre_ids:
            break
    request = request_factory.get(f"/albums/{album_id}/genres/{genre_id}")
    response = single_album_single_genre(request, album_id, genre_id)
    assert response.status_code == 404
    json_content = json_loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f"no genre with genre_id={genre_id}"


@pytest.mark.django_db
def test_single_album_single_genre_GET_error_album_not_assoc_w_genre():
    album_ids = [album.album_id for album in Album.objects.filter()]
    genre_ids = [genre.genre_id for genre in Genre.objects.filter()]
    while True:
        album_id = random.choice(album_ids)
        genre_id = random.choice(genre_ids)
        try:
            bridge_row = AlbumGenreBridge.objects.get(album_id=album_id, genre_id=genre_id)
        except AlbumGenreBridge.DoesNotExist:
            break;
    request = request_factory.get(f"/albums/{album_id}/genres/{genre_id}")
    response = single_album_single_genre(request, album_id, genre_id)
    assert response.status_code == 404
    json_content = json_loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f'album with album_id={album_id} not associated with genre with genre_id={genre_id}'


@pytest.mark.django_db
def test_single_album_single_genre_DELETE():
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    bridge_rows = AlbumGenreBridge.objects.filter(album_id=album_id)
    bridge_row = random.choice(bridge_rows)
    genre = Genre.objects.get(genre_id=bridge_row.genre_id)
    genre_id = genre.genre_id
    request = request_factory.delete(f"/albums/{album_id}/genres/{genre_id}")
    response = single_album_single_genre(request, album_id, genre_id)
    json_content = json_loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f'association between album with album_id={album_id} and genre with genre_id={genre_id} deleted'
    try:
        AlbumGenreBridge.objects.get(album_id=album_id, genre_id=genre_id)
        pytest.fail()
    except AlbumGenreBridge.DoesNotExist as exception:
        assert isinstance(exception, AlbumGenreBridge.DoesNotExist)


@pytest.mark.django_db
def test_single_album_single_genre_DELETE_error_nonexistent_album_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    while True:
        album_id = random.randint(1,9999)
        if album_id not in album_ids:
            break
    genre_ids = [genre.genre_id for genre in Genre.objects.filter()]
    genre_id = random.choice(genre_ids)
    request = request_factory.delete(f"/albums/{album_id}/genres/{genre_id}")
    response = single_album_single_genre(request, album_id, genre_id)
    assert response.status_code == 404
    json_content = json_loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f"no album with album_id={album_id}"


@pytest.mark.django_db
def test_single_album_single_genre_DELETE_error_nonexistent_genre_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    album_id = random.choice(album_ids)
    genre_ids = [genre.genre_id for genre in Genre.objects.filter()]
    while True:
        genre_id = random.randint(1,99)
        if genre_id not in genre_ids:
            break
    request = request_factory.delete(f"/albums/{album_id}/genres/{genre_id}")
    response = single_album_single_genre(request, album_id, genre_id)
    assert response.status_code == 404
    json_content = json_loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f"no genre with genre_id={genre_id}"


@pytest.mark.django_db
def test_single_album_single_genre_DELETE_error_album_not_assoc_w_genre():
    album_ids = [album.album_id for album in Album.objects.filter()]
    genre_ids = [genre.genre_id for genre in Genre.objects.filter()]
    while True:
        album_id = random.choice(album_ids)
        genre_id = random.choice(genre_ids)
        try:
            bridge_row = AlbumGenreBridge.objects.get(album_id=album_id, genre_id=genre_id)
        except AlbumGenreBridge.DoesNotExist:
            break;
    request = request_factory.delete(f"/albums/{album_id}/genres/{genre_id}")
    response = single_album_single_genre(request, album_id, genre_id)
    assert response.status_code == 404
    json_content = json_loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f'album with album_id={album_id} not associated with genre with genre_id={genre_id}'





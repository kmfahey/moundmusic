#!/usr/bin/python3

import pytest
import re
import random
import json

from django.test.client import RequestFactory
from django.http.response import JsonResponse

from .models import Album, AlbumGenreBridge, AlbumSongBridge, Artist, ArtistAlbumBridge, Genre, Song

from .views import index, single_album, single_album_songs, single_album_single_song, single_album_genres, \
        single_album_single_genre, single_album_artists, single_album_single_artist

request_factory = RequestFactory()

matches_date_isoformat = lambda strval: bool(re.match(r"^\d{4}-\d{2}-\d{2}$", strval))


@pytest.mark.django_db
def test_index_GET():
    request = request_factory.get("/albums/")
    response = index(request)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert len(json_content)
    assert isinstance(json_content, list)
    sample_album_jsobject = json_content[0]
    assert "album_id" in sample_album_jsobject and isinstance(sample_album_jsobject.get("album_id"), int)
    assert "title" in sample_album_jsobject and isinstance(sample_album_jsobject.get("title"), str)
    assert "number_of_discs" in sample_album_jsobject and isinstance(sample_album_jsobject.get("number_of_discs"), int)
    assert "number_of_tracks" in sample_album_jsobject
    assert isinstance(sample_album_jsobject.get("number_of_tracks"), int)
    assert "release_date" in sample_album_jsobject and isinstance(sample_album_jsobject.get("release_date"), str)
    assert matches_date_isoformat(sample_album_jsobject["release_date"])


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
    json_content = json.loads(response.content)
    assert len(json_content)
    assert isinstance(json_content, dict)
    try:
        new_test_album = Album.objects.get(album_id=json_content["album_id"])
    except (KeyError, Album.DoesNotExist):
        pytest.fail()
    assert new_test_album.title == new_album_dict["title"]
    assert new_test_album.number_of_discs == new_album_dict["number_of_discs"]
    assert new_test_album.number_of_tracks == new_album_dict["number_of_tracks"]
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
    json_content = json.loads(response.content)
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
    max_album_id = max(album.album_id for album in Album.objects.filter())
    album = Album(album_id=max_album_id, **new_album_dict)
    album.save()
    album_id = album.album_id
    request = request_factory.get(f"/albums/{album_id}")
    response = single_album(request, album_id)
    json_content = json.loads(response.content)
    assert json_content["title"] == album.title
    assert json_content["number_of_discs"] == album.number_of_discs
    assert json_content["number_of_tracks"] == album.number_of_tracks
    assert json_content["release_date"] == album.release_date
    assert matches_date_isoformat(json_content["release_date"])
    assert json_content["album_id"] == album.album_id


@pytest.mark.django_db
def test_single_album_GET_error_nonexistent_album_id():
    albums = Album.objects.filter()
    album_ids = [album.album_id for album in albums]
    while True:
        album_id = random.randint(1, 9999)
        if album_id not in album_ids:
            break
    request = request_factory.get(f"/albums/{album_id}")
    response = single_album(request, album_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] == f'no album with album_id={album_id}'


@pytest.mark.django_db
def test_single_album_PATCH():
    new_album_dict = {
        "title": "Some Album",
        "number_of_discs": 1,
        "number_of_tracks": 12,
        "release_date": "1998-01-01"
    }
    max_album_id = max(album.album_id for album in Album.objects.filter())
    album = Album(album_id=max_album_id + 1, **new_album_dict)
    album.save()
    album_id = album.album_id
    album_patch_dict = {"title": "Some Other Album"}
    request = request_factory.patch(f"/albums/{album_id}", data=album_patch_dict, content_type="application/json")
    response = single_album(request, album_id)
    json_content = json.loads(response.content)
    album = Album.objects.get(album_id=album_id)
    assert json_content["title"] == "Some Other Album"
    assert json_content["number_of_discs"] == new_album_dict["number_of_discs"]
    assert json_content["number_of_tracks"] == new_album_dict["number_of_tracks"]
    assert json_content["release_date"] == new_album_dict["release_date"]
    assert album.title == "Some Other Album"
    assert album.number_of_discs == new_album_dict["number_of_discs"]
    assert album.number_of_tracks == new_album_dict["number_of_tracks"]
    assert album.release_date.isoformat() == new_album_dict["release_date"]


@pytest.mark.django_db
def test_single_album_PATCH_error_nonexistent_album_id():
    album_patch_dict = {"title": "Foo"}
    albums = Album.objects.filter()
    album_ids = [album.album_id for album in albums]
    while True:
        album_id = random.randint(1, 9999)
        if album_id not in album_ids:
            break
    request = request_factory.patch(f"/albums/{album_id}", data=album_patch_dict, content_type="application/json")
    response = single_album(request, album_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] == f'no album with album_id={album_id}'


@pytest.mark.django_db
def test_single_album_PATCH_error_invalid_args():
    album_patch_dict = {"title": ""}
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    request = request_factory.patch(f"/albums/{album_id}", data=album_patch_dict, content_type="application/json")
    response = single_album(request, album_id)
    assert response.status_code == 400
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert len(json_content)
    assert isinstance(json_content, dict)
    assert json_content['message'] == "value for 'title' is a string of zero length"


@pytest.mark.django_db
def test_single_album_DELETE():
    album = Album.objects.filter()[0]
    album_id = album.album_id
    request = request_factory.delete(f"/albums/{album_id}")
    response = single_album(request, album_id)
    json_content = json.loads(response.content)
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
        album_id = random.randint(1, 9999)
        if album_id not in album_ids:
            break
    request = request_factory.delete(f"/albums/{album_id}")
    response = single_album(request, album_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
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
    json_content = json.loads(response.content)
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
        album_id = random.randint(1, 9999)
        if album_id not in album_ids:
            break
    request = request_factory.get(f"/albums/{album_id}/songs")
    response = single_album_songs(request, album_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
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
    json_content = json.loads(response.content)
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
        album_id = random.randint(1, 9999)
        if album_id not in album_ids:
            break
    song_ids = [song.song_id for song in Song.objects.filter()]
    while True:
        song_id = random.randint(1, 9999)
        if song_id not in song_ids:
            break
    request = request_factory.get(f"/albums/{album_id}/songs/{song_id}")
    response = single_album_single_song(request, album_id, song_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f'no album with album_id={album_id}'


@pytest.mark.django_db
def test_single_album_genres_GET():
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    request = request_factory.get(f"/albums/{album_id}/genres")
    response = single_album_genres(request, album_id)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert isinstance(json_content, list)
    sample_genre_dict = random.choice(json_content)
    assert 'genre_id' in sample_genre_dict and isinstance(sample_genre_dict['genre_id'], int)
    assert 'genre_name' in sample_genre_dict and isinstance(sample_genre_dict['genre_name'], str)


@pytest.mark.django_db
def test_single_album_genres_GET_error_nonexistent_album_id():
    albums = Album.objects.filter()
    album_ids = [album.album_id for album in albums]
    while True:
        album_id = random.randint(1, 9999)
        if album_id not in album_ids:
            break
    request = request_factory.get(f"/albums/{album_id}/genres")
    response = single_album_genres(request, album_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f'no album with album_id={album_id}'


@pytest.mark.django_db
def test_single_album_genres_POST():
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    bridge_rows = AlbumGenreBridge.objects.filter(album_id=album_id)
    album_assoc_w_genre_ids = [bridge_row.genre_id for bridge_row in bridge_rows]
    genres = Genre.objects.filter()
    while True:
        genre = random.choice(genres)
        genre_id = genre.genre_id
        if genre_id not in album_assoc_w_genre_ids:
            break
    new_genre_assoc_dict = {"genre_id": genre_id}
    request = request_factory.post(f"/albums/{album_id}/genres",
                                   data=new_genre_assoc_dict,
                                   content_type="application/json")
    response = single_album_genres(request, album_id)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert len(json_content)
    assert isinstance(json_content, dict)
    assert 'genre_id' in json_content and json_content['genre_id'] == genre.genre_id
    assert 'genre_name' in json_content and json_content['genre_name'] == genre.genre_name
    bridge_rows = AlbumGenreBridge.objects.filter(album_id=album_id)
    assert any(bridge_row.genre_id == genre_id for bridge_row in bridge_rows)


@pytest.mark.django_db
def test_single_album_genres_POST_error_nonexistent_album_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    while True:
        album_id = random.randint(1, 9999)
        if album_id not in album_ids:
            break
    genre_ids = [genre.genre_id for genre in Genre.objects.filter()]
    genre_id = random.choice(genre_ids)
    new_genre_assoc_dict = {"genre_id": genre_id}
    request = request_factory.post(f"/albums/{album_id}/genres",
                                   data=new_genre_assoc_dict,
                                   content_type="application/json")
    response = single_album_genres(request, album_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f"no album with album_id={album_id}"


@pytest.mark.django_db
def test_single_album_genres_POST_error_nonexistent_genre_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    album_id = random.choice(album_ids)
    genre_ids = [genre.genre_id for genre in Genre.objects.filter()]
    while True:
        genre_id = random.randint(1, 99)
        if genre_id not in genre_ids:
            break
    new_genre_assoc_dict = {"genre_id": genre_id}
    request = request_factory.post(f"/albums/{album_id}/genres",
                                   data=new_genre_assoc_dict,
                                   content_type="application/json")
    response = single_album_genres(request, album_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f"no genre with genre_id={genre_id}"


@pytest.mark.django_db
def test_single_album_genres_POST_error_bridge_row_already_exists():
    album_ids = [album.album_id for album in Album.objects.filter()]
    album_id = random.choice(album_ids)
    bridge_rows = AlbumGenreBridge.objects.filter(album_id=album_id)
    bridge_row = random.choice(bridge_rows)
    genre_id = bridge_row.genre_id
    existing_genre_assoc_dict = {"genre_id": genre_id}
    request = request_factory.post(f"/albums/{album_id}/genres",
                                   data=existing_genre_assoc_dict,
                                   content_type="application/json")
    response = single_album_genres(request, album_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 400
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == (f"association between album with album_id={album_id} and "
                                       f"genre with genre_id={genre_id} already exists")


@pytest.mark.django_db
def test_single_album_genres_POST_error_invalid_args():
    album_ids = [album.album_id for album in Album.objects.filter()]
    album_id = random.choice(album_ids)
    genre_ids = [genre.genre_id for genre in Genre.objects.filter()]
    genre_id = random.choice(genre_ids)
    new_genre_assoc_dict = {"genre_id": genre_id, "foo": "bar"}
    request = request_factory.post(f"/albums/{album_id}/genres",
                                   data=new_genre_assoc_dict,
                                   content_type="application/json")
    response = single_album_genres(request, album_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 400
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == "unexpected property in input: 'foo'"


#--
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
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == (f'association between album with album_id={album_id} '
                                       f'and song with song_id={song_id} deleted')
    try:
        AlbumSongBridge.objects.get(album_id=album_id, song_id=song_id)
        pytest.fail()
    except AlbumSongBridge.DoesNotExist as exception:
        assert isinstance(exception, AlbumSongBridge.DoesNotExist)


@pytest.mark.django_db
def test_single_album_single_song_DELETE_error_nonexistent_album_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    while True:
        album_id = random.randint(1, 9999)
        if album_id not in album_ids:
            break
    song_ids = [song.song_id for song in Song.objects.filter()]
    song_id = random.choice(song_ids)
    request = request_factory.delete(f"/albums/{album_id}/songs/{song_id}")
    response = single_album_single_song(request, album_id, song_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f"no album with album_id={album_id}"


@pytest.mark.django_db
def test_single_album_single_song_DELETE_error_nonexistent_song_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    album_id = random.choice(album_ids)
    song_ids = [song.song_id for song in Song.objects.filter()]
    while True:
        song_id = random.randint(1, 9999)
        if song_id not in song_ids:
            break
    request = request_factory.delete(f"/albums/{album_id}/songs/{song_id}")
    response = single_album_single_song(request, album_id, song_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f"no song with song_id={song_id}"


@pytest.mark.django_db
def test_single_album_single_song_DELETE_error_album_not_assoc_w_song():
    album_ids = [album.album_id for album in Album.objects.filter()]
    song_ids = [song.song_id for song in Song.objects.filter()]
    while True:
        album_id = random.choice(album_ids)
        song_id = random.choice(song_ids)
        try:
            AlbumSongBridge.objects.get(album_id=album_id, song_id=song_id)
        except AlbumSongBridge.DoesNotExist:
            break
    request = request_factory.delete(f"/albums/{album_id}/songs/{song_id}")
    response = single_album_single_song(request, album_id, song_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == (f'album with album_id={album_id} not associated with '
                                       f'song with song_id={song_id}')


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
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == (f'association between album with album_id={album_id} '
                                       f'and genre with genre_id={genre_id} deleted')
    try:
        AlbumGenreBridge.objects.get(album_id=album_id, genre_id=genre_id)
        pytest.fail()
    except AlbumGenreBridge.DoesNotExist as exception:
        assert isinstance(exception, AlbumGenreBridge.DoesNotExist)


@pytest.mark.django_db
def test_single_album_single_genre_DELETE_error_nonexistent_album_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    while True:
        album_id = random.randint(1, 9999)
        if album_id not in album_ids:
            break
    genre_ids = [genre.genre_id for genre in Genre.objects.filter()]
    genre_id = random.choice(genre_ids)
    request = request_factory.delete(f"/albums/{album_id}/genres/{genre_id}")
    response = single_album_single_genre(request, album_id, genre_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f"no album with album_id={album_id}"


@pytest.mark.django_db
def test_single_album_single_genre_DELETE_error_nonexistent_genre_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    album_id = random.choice(album_ids)
    genre_ids = [genre.genre_id for genre in Genre.objects.filter()]
    while True:
        genre_id = random.randint(1, 99)
        if genre_id not in genre_ids:
            break
    request = request_factory.delete(f"/albums/{album_id}/genres/{genre_id}")
    response = single_album_single_genre(request, album_id, genre_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
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
            AlbumGenreBridge.objects.get(album_id=album_id, genre_id=genre_id)
        except AlbumGenreBridge.DoesNotExist:
            break
    request = request_factory.delete(f"/albums/{album_id}/genres/{genre_id}")
    response = single_album_single_genre(request, album_id, genre_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == (f'album with album_id={album_id} not associated with '
                                       f'genre with genre_id={genre_id}')


@pytest.mark.django_db
def test_single_album_artists_GET():
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    request = request_factory.get(f"/albums/{album_id}/artists")
    response = single_album_artists(request, album_id)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert len(json_content)
    assert isinstance(json_content, list)
    sample_artist_dict = random.choice(json_content)
    assert 'artist_id' in sample_artist_dict and isinstance(sample_artist_dict['artist_id'], int)
    assert 'first_name' in sample_artist_dict and isinstance(sample_artist_dict['first_name'], str)
    assert 'last_name' in sample_artist_dict and isinstance(sample_artist_dict['last_name'], str)
    assert 'gender' in sample_artist_dict and sample_artist_dict['gender'] in ('male', 'female', 'nonbinary')
    assert 'birth_date' in sample_artist_dict and matches_date_isoformat(sample_artist_dict['birth_date'])


@pytest.mark.django_db
def test_single_album_artists_GET_error_nonexistent_album_id():
    albums = Album.objects.filter()
    album_ids = [album.album_id for album in albums]
    while True:
        album_id = random.randint(1, 9999)
        if album_id not in album_ids:
            break
    request = request_factory.get(f"/albums/{album_id}/artists")
    response = single_album_artists(request, album_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f'no album with album_id={album_id}'


@pytest.mark.django_db
def test_single_album_artists_POST():
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    bridge_rows = ArtistAlbumBridge.objects.filter(album_id=album_id)
    album_already_in_artist_ids = [bridge_row.artist_id for bridge_row in bridge_rows]
    while True:
        artist = random.choice(Artist.objects.filter())
        artist_id = artist.artist_id
        if artist_id not in album_already_in_artist_ids:
            break
    new_artist_assoc_dict = {"artist_id": artist_id}
    request = request_factory.post(f"/albums/{album_id}/artists",
                                   data=new_artist_assoc_dict,
                                   content_type="application/json")
    response = single_album_artists(request, album_id)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert len(json_content)
    assert isinstance(json_content, dict)
    assert 'artist_id' in json_content and json_content['artist_id'] == artist.artist_id
    assert 'first_name' in json_content and json_content['first_name'] == artist.first_name
    assert 'last_name' in json_content and json_content['last_name'] == artist.last_name
    assert 'gender' in json_content and json_content['gender'] == artist.gender
    assert 'birth_date' in json_content and json_content['birth_date'] == artist.birth_date.isoformat()
    bridge_rows = ArtistAlbumBridge.objects.filter(album_id=album_id)
    assert any(bridge_row.artist_id == artist_id for bridge_row in bridge_rows)


@pytest.mark.django_db
def test_single_album_artists_POST_error_nonexistent_album_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    while True:
        album_id = random.randint(1, 9999)
        if album_id not in album_ids:
            break
    artist_ids = [artist.artist_id for artist in Artist.objects.filter()]
    artist_id = random.choice(artist_ids)
    new_artist_assoc_dict = {"artist_id": artist_id}
    request = request_factory.post(f"/albums/{album_id}/artists",
                                   data=new_artist_assoc_dict,
                                   content_type="application/json")
    response = single_album_artists(request, album_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f"no album with album_id={album_id}"


@pytest.mark.django_db
def test_single_album_artists_POST_error_nonexistent_artist_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    album_id = random.choice(album_ids)
    artist_ids = [artist.artist_id for artist in Artist.objects.filter()]
    while True:
        artist_id = random.randint(1, 99)
        if artist_id not in artist_ids:
            break
    new_artist_assoc_dict = {"artist_id": artist_id}
    request = request_factory.post(f"/albums/{album_id}/artists",
                                   data=new_artist_assoc_dict,
                                   content_type="application/json")
    response = single_album_artists(request, album_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f"no artist with artist_id={artist_id}"


@pytest.mark.django_db
def test_single_album_artists_POST_error_bridge_row_already_exists():
    while True:
        album_ids = [album.album_id for album in Album.objects.filter()]
        album_id = random.choice(album_ids)
        bridge_rows = ArtistAlbumBridge.objects.filter(album_id=album_id)
        if len(bridge_rows):
            bridge_row = random.choice(bridge_rows)
            break
    artist_id = bridge_row.artist_id
    existing_artist_assoc_dict = {"artist_id": artist_id}
    request = request_factory.post(f"/albums/{album_id}/artists",
                                   data=existing_artist_assoc_dict,
                                   content_type="application/json")
    response = single_album_artists(request, album_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 400
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == (f"association between album with album_id={album_id} and "
                                       f"artist with artist_id={artist_id} already exists")


@pytest.mark.django_db
def test_single_album_artists_POST_error_invalid_args():
    album_ids = [album.album_id for album in Album.objects.filter()]
    album_id = random.choice(album_ids)
    artist_ids = [artist.artist_id for artist in Artist.objects.filter()]
    artist_id = random.choice(artist_ids)
    new_artist_assoc_dict = {"artist_id": artist_id, "foo": "bar"}
    request = request_factory.post(f"/albums/{album_id}/artists",
                                   data=new_artist_assoc_dict,
                                   content_type="application/json")
    response = single_album_artists(request, album_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 400
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == "unexpected property in input: 'foo'"


@pytest.mark.django_db
def test_single_album_single_artist_DELETE():
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    bridge_rows = ArtistAlbumBridge.objects.filter(album_id=album_id)
    bridge_row = random.choice(bridge_rows)
    artist = Artist.objects.get(artist_id=bridge_row.artist_id)
    artist_id = artist.artist_id
    request = request_factory.delete(f"/albums/{album_id}/artists/{artist_id}")
    response = single_album_single_artist(request, album_id, artist_id)
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == (f'association between album with album_id={album_id} '
                                       f'and artist with artist_id={artist_id} deleted')
    try:
        ArtistAlbumBridge.objects.get(album_id=album_id, artist_id=artist_id)
        pytest.fail()
    except ArtistAlbumBridge.DoesNotExist as exception:
        assert isinstance(exception, ArtistAlbumBridge.DoesNotExist)


@pytest.mark.django_db
def test_single_album_single_artist_DELETE_error_nonexistent_album_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    while True:
        album_id = random.randint(1, 9999)
        if album_id not in album_ids:
            break
    artist_ids = [artist.artist_id for artist in Artist.objects.filter()]
    artist_id = random.choice(artist_ids)
    request = request_factory.delete(f"/albums/{album_id}/artists/{artist_id}")
    response = single_album_single_artist(request, album_id, artist_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f"no album with album_id={album_id}"


@pytest.mark.django_db
def test_single_album_single_artist_DELETE_error_nonexistent_artist_id():
    album_ids = [album.album_id for album in Album.objects.filter()]
    album_id = random.choice(album_ids)
    artist_ids = [artist.artist_id for artist in Artist.objects.filter()]
    while True:
        artist_id = random.randint(1, 99)
        if artist_id not in artist_ids:
            break
    request = request_factory.delete(f"/albums/{album_id}/artists/{artist_id}")
    response = single_album_single_artist(request, album_id, artist_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == f"no artist with artist_id={artist_id}"


@pytest.mark.django_db
def test_single_album_single_artist_DELETE_error_album_not_assoc_w_artist():
    album_ids = [album.album_id for album in Album.objects.filter()]
    artist_ids = [artist.artist_id for artist in Artist.objects.filter()]
    while True:
        album_id = random.choice(album_ids)
        artist_id = random.choice(artist_ids)
        try:
            ArtistAlbumBridge.objects.get(album_id=album_id, artist_id=artist_id)
        except ArtistAlbumBridge.DoesNotExist:
            break
    request = request_factory.delete(f"/albums/{album_id}/artists/{artist_id}")
    response = single_album_single_artist(request, album_id, artist_id)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert 'message' in json_content
    assert json_content['message'] == (f'album with album_id={album_id} not associated '
                                       f'with artist with artist_id={artist_id}')

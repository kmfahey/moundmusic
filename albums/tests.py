#!/usr/bin/python3

import pytest

from re import match as re_match

from datetime import date

from json import loads as parse_json

from django.test.client import RequestFactory
from django.http.response import JsonResponse

from .views import index


request_factory = RequestFactory()

@pytest.mark.django_db
def test_index_GET():
    request = request_factory.get("/albums/")
    response = index(request)
    assert isinstance(response, JsonResponse)
    json_content = parse_json(response.content)
    assert len(json_content)
    assert isinstance(json_content, list)
    sample_album_jsobject = json_content[0]
    assert "album_id" in sample_album_jsobject
    assert "title" in sample_album_jsobject
    assert "number_of_discs" in sample_album_jsobject
    assert "number_of_tracks" in sample_album_jsobject
    assert "release_date" in sample_album_jsobject
    assert "album_cover_id" in sample_album_jsobject
    assert isinstance(sample_album_jsobject.get("album_id"), int)
    assert isinstance(sample_album_jsobject.get("title"), str)
    assert isinstance(sample_album_jsobject.get("number_of_discs"), int)
    assert isinstance(sample_album_jsobject.get("number_of_tracks"), int)
    assert isinstance(sample_album_jsobject.get("release_date"), str) and re_match(r"^\d{4}-\d{2}-\d{2}$", sample_album_jsobject.get("release_date"))
    assert isinstance(sample_album_jsobject.get("album_cover_id"), int)



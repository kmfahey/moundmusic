#!/usr/bin/python3

from django.http.response import JsonResponse

from rest_framework import status
from rest_framework.decorators import api_view

from moundmusic.viewutils import dispatch_funcs_by_method, validate_post_request
from moundmusic.viewutils import define_GET_POST_index_closure, define_single_model_GET_PATCH_DELETE_closure

from .models import Artist


index = define_GET_POST_index_closure(Artist)


single_artist = define_single_model_GET_PATCH_DELETE_closure(Artist, 'artist_id')


single_artist_albums = define_single_outer_model_all_of_inner_model_GET_POST_closure(Album, 'artist_id', Genre, 'album_id', ArtistAlbumBridge)


single_artist_single_album = define_single_outer_model_single_inner_model_GET_DELETE_closure(Artist, 'artist_id', Album, 'album_id', ArtistAlbumBridge)



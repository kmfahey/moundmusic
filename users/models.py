#!/usr/bin/python

from django.db import models

from albums.models import Album, AlbumGenreBridge, AlbumSongBridge, Artist, ArtistAlbumBridge, ArtistGenreBridge, \
        ArtistSongBridge, BuyerAccount, Genre, SellerAccount, Song, SongGenreBridge, SongLyrics, ToBuyListing, \
        ToSellListing, User, UserPassword


for model_class in (Album, AlbumGenreBridge, AlbumSongBridge, Artist, ArtistAlbumBridge, ArtistGenreBridge,
                    ArtistSongBridge, BuyerAccount, Genre, SellerAccount, Song, SongGenreBridge, SongLyrics,
                    ToBuyListing, ToSellListing, User, UserPassword):
    model_class._meta.app_label = "users"


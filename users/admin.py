#!/usr/bin/python

from django.contrib import admin

from .models import Album, AlbumGenreBridge, AlbumSongBridge, Artist, ArtistAlbumBridge, ArtistGenreBridge, \
        ArtistSongBridge, BuyerAccount, Genre, SellerAccount, Song, SongGenreBridge, SongLyrics, ToBuyListing, \
        ToSellListing, User, UserPassword


for model_class in (Album, AlbumGenreBridge, AlbumSongBridge, Artist, ArtistAlbumBridge, ArtistGenreBridge,
                    ArtistSongBridge, BuyerAccount, Genre, SellerAccount, Song, SongGenreBridge, SongLyrics,
                    ToBuyListing, ToSellListing, User, UserPassword):
    admin.site.register(model_class)



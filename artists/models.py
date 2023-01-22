#!/usr/bin/python

from albums.models import Album, AlbumGenreBridge, AlbumSongBridge, Artist, ArtistAlbumBridge, ArtistGenreBridge, \
        ArtistSongBridge, BuyerAccount, Genre, SellerAccount, Song, SongGenreBridge, SongLyrics, ToBuyListing, \
        ToSellListing, User, UserPassword


# This package reuses models between apps, through the simple expedient of
# importing them and setting their ._meta.app_label to this app's name.

for model_class in (Album, AlbumGenreBridge, AlbumSongBridge, Artist, ArtistAlbumBridge, ArtistGenreBridge,
                    ArtistSongBridge, BuyerAccount, Genre, SellerAccount, Song, SongGenreBridge, SongLyrics,
                    ToBuyListing, ToSellListing, User, UserPassword):
    model_class._meta.app_label = "artists"

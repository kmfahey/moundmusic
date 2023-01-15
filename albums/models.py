#!/usr/bin/python3

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
# Feel free to rename the models, but don't rename db_table values or field names.

import codecs

from datetime import date
from django.db import models



class serializable(object):
    def serialize(self):
        serialization = dict()
        for column in self.__columns__.keys():
            column_value = getattr(self, column)
            if isinstance(column_value, bytes):
                column_value = codecs.decode(column_value)
            serialization[column] = column_value
        return serialization


class Album(models.Model, serializable):
    __columns__ = {'album_id': int, 'title': str, 'number_of_discs': int, 'number_of_tracks': int, 'release_date': date}
    __nullable_cols__ = ('album_id',)

    album_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    number_of_discs = models.SmallIntegerField()
    number_of_tracks = models.SmallIntegerField()
    release_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        managed = False
        db_table = 'album'
        app_label = 'albums'


class AlbumGenreBridge(models.Model):
    album_genre_bridge_id = models.AutoField(primary_key=True)
    album = models.ForeignKey(Album, models.CASCADE, blank=True, null=True)
    genre = models.ForeignKey('Genre', models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'album_genre_bridge'
        app_label = 'albums'


class AlbumSongBridge(models.Model):
    album_song_bridge_id = models.AutoField(primary_key=True)
    album = models.ForeignKey(Album, models.CASCADE, blank=True, null=True)
    disc_number = models.SmallIntegerField()
    track_number = models.SmallIntegerField()
    song = models.ForeignKey('Song', models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'album_song_bridge'
        app_label = 'albums'


class Artist(models.Model, serializable):
    __columns__ = {'artist_id': int, 'first_name': str, 'last_name': str, 'gender': ('male','female','nonbinary'),
                   'birth_date': date}
    __nullable_cols__ = ()

    artist_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    # The column below is actually a ENUM('male', 'female', 'nonbinary')
    # postgresql custom type, but django can't handle those. So long as it's
    # only ever set to (png|jpg|gif) there won't be any problems leaving it as a
    # TextField.
    gender = models.TextField()  # This field type is a guess.
    birth_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'artist'
        app_label = 'albums'


class ArtistAlbumBridge(models.Model):
    artist_album_bridge_id = models.AutoField(primary_key=True)
    album = models.ForeignKey(Album, models.CASCADE, blank=True, null=True)
    artist = models.ForeignKey(Artist, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'artist_album_bridge'
        app_label = 'albums'


class ArtistGenreBridge(models.Model):
    artist_genre_bridge_id = models.AutoField(primary_key=True)
    artist = models.ForeignKey(Artist, models.CASCADE, blank=True, null=True)
    genre = models.ForeignKey('Genre', models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'artist_genre_bridge'
        app_label = 'albums'


class ArtistSongBridge(models.Model):
    artist_song_bridge_id = models.AutoField(primary_key=True)
    song = models.ForeignKey('Song', models.CASCADE, blank=True, null=True)
    artist = models.ForeignKey(Artist, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'artist_song_bridge'
        app_label = 'albums'


class BuyerAccount(models.Model, serializable):
    __columns__ = {'buyer_id': int, 'postboard_name': str, 'date_created': date, 'user_id': int}
    __nullable_cols__ = ('buyer_id', 'user_id')

    buyer_id = models.AutoField(primary_key=True)
    postboard_name = models.CharField(max_length=64, blank=True, null=True)
    date_created = models.DateField()
    user = models.ForeignKey('User', models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'buyer_account'
        app_label = 'albums'


class Genre(models.Model, serializable):
    __columns__ = {'genre_id': int, 'genre_name': str}
    __nullable_cols__ = ('genre_id',)

    genre_id = models.AutoField(primary_key=True)
    genre_name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'genre'
        app_label = 'albums'


class SellerAccount(models.Model, serializable):
    __columns__ = {'seller_id': int, 'storefront_name': str, 'date_created': date, 'user_id': int}
    __nullable_cols__ = ('seller_id', 'user_id')

    seller_id = models.AutoField(primary_key=True)
    storefront_name = models.CharField(max_length=64, blank=True, null=True)
    date_created = models.DateField()
    user = models.ForeignKey('User', models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'seller_account'
        app_label = 'albums'


class Song(models.Model, serializable):
    __columns__ = {'song_id': int, 'title': str, 'length_minutes': int, 'length_seconds': int, 'song_lyrics_id': int}
    __nullable_cols__ = ('song_id', 'song_lyrics_id')

    song_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    length_minutes = models.SmallIntegerField()
    length_seconds = models.SmallIntegerField()
    song_lyrics = models.ForeignKey('SongLyrics', models.CASCADE, blank=True, null=True, related_name="+")

    class Meta:
        managed = False
        db_table = 'song'
        app_label = 'albums'


class SongGenreBridge(models.Model):
    song_genre_bridge_id = models.AutoField(primary_key=True)
    song = models.ForeignKey(Song, models.CASCADE, blank=True, null=True)
    genre = models.ForeignKey(Genre, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'song_genre_bridge'
        app_label = 'albums'


class SongLyrics(models.Model, serializable):
    __columns__ = {'song_lyrics_id': int, 'lyrics': str, 'song_id': int}
    __nullable_cols__ = ('song_lyrics_id', 'song_id')

    song_lyrics_id = models.AutoField(primary_key=True)
    lyrics = models.TextField()
    song = models.ForeignKey(Song, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'song_lyrics'
        app_label = 'albums'


class ToBuyListing(models.Model, serializable):
    __columns__ = {'to_buy_listing_id': int, 'max_accepting_price': str, 'date_posted': date, 'album_id': int, 'buyer_id': int}
    __nullable_cols__ = ('to_buy_listing_id',)

    to_buy_listing_id = models.AutoField(primary_key=True)
    max_accepting_price = models.DecimalField(max_digits=65535, decimal_places=65535)
    date_posted = models.DateField(blank=True, null=True)
    album = models.ForeignKey(Album, models.CASCADE, blank=True, null=True)
    buyer = models.ForeignKey(BuyerAccount, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'to_buy_listing'
        app_label = 'albums'


class ToSellListing(models.Model, serializable):
    __columns__ = {'to_sell_listing_id': int, 'asking_price': str, 'date_posted': date, 'album_id': int, 'seller_id': int}
    __nullable_cols__ = ('to_sell_listing_id',)

    to_sell_listing_id = models.AutoField(primary_key=True)
    asking_price = models.DecimalField(max_digits=65535, decimal_places=65535)
    date_posted = models.DateField(blank=True, null=True)
    album = models.ForeignKey(Album, models.CASCADE, blank=True, null=True)
    seller = models.ForeignKey(SellerAccount, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'to_sell_listing'
        app_label = 'albums'


class User(models.Model, serializable):
    __columns__ = {'user_id': int, 'user_name': str, 'first_name': str, 'last_name': str,
                   'gender': ('male','female','nonbinary'), 'date_joined': date, 'buyer_id': int, 'seller_id': int}
    __nullable_cols__ = ('user_id', 'buyer_id', 'seller_id')

    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=16)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    # The column below is actually a ENUM('male', 'female', 'nonbinary')
    # postgresql custom type, but django can't handle those. So long as it's
    # only ever set to (png|jpg|gif) there won't be any problems leaving it as a
    # TextField.
    gender = models.TextField()  # This field type is a guess.
    date_joined = models.DateField()
    buyer_id = models.IntegerField(blank=True, null=True)
    seller_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_'
        app_label = 'albums'


class UserPassword(models.Model, serializable):
    __columns__ = {'password_id': int, 'encrypted_password': str, 'user_id': int}
    __nullable_cols__ = ('password_id', 'user_id')

    password_id = models.AutoField(primary_key=True)
    encrypted_password = models.BinaryField()
    user = models.ForeignKey(User, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_password'
        app_label = 'albums'

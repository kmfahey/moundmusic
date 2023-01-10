# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

import django

from django.db import models


class Album(models.Model):
    album_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    number_of_discs = models.SmallIntegerField()
    number_of_tracks = models.SmallIntegerField()
    release_date = models.DateField(blank=True, null=True)
    album_cover = models.ForeignKey('AlbumCover', models.SET_NULL, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'album'
        app_label = 'albums'


class AlbumCover(models.Model):
    album_cover_id = models.AutoField(primary_key=True)
    # The column below is actually a ENUM('png', 'jpg', 'gif') postgresql custom
    # type, but django can't handle those. So long as it's only ever set to
    # (png|jpg|gif) there won't be any problems leaving it as a TextField.
    image_file_type = models.TextField()  # This field type is a guess.
    image_data = models.BinaryField()
    src_album = models.ForeignKey(Album, models.SET_NULL, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'album_cover'
        app_label = 'albums'


class AlbumGenreBridge(models.Model):
    album_genre_bridge_id = models.AutoField(primary_key=True)
    album = models.ForeignKey(Album, models.SET_NULL, blank=True, null=True)
    genre = models.ForeignKey('Genre', models.SET_NULL, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'album_genre_bridge'
        app_label = 'albums'


class AlbumSongBridge(models.Model):
    album_song_bridge_id = models.AutoField(primary_key=True)
    album = models.ForeignKey(Album, models.SET_NULL, blank=True, null=True)
    disc_number = models.SmallIntegerField()
    track_number = models.SmallIntegerField()
    song = models.ForeignKey('Song', models.SET_NULL, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'album_song_bridge'
        app_label = 'albums'


class Artist(models.Model):
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
    artists_albums_id = models.AutoField(primary_key=True)
    album = models.ForeignKey(Album, models.SET_NULL, blank=True, null=True)
    artist = models.ForeignKey(Artist, models.SET_NULL, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'artist_album_bridge'
        app_label = 'albums'


class ArtistGenreBridge(models.Model):
    artists_genres_id = models.AutoField(primary_key=True)
    artist = models.ForeignKey(Artist, models.SET_NULL, blank=True, null=True)
    genre = models.ForeignKey('Genre', models.SET_NULL, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'artist_genre_bridge'
        app_label = 'albums'


class ArtistSongBridge(models.Model):
    artist_song_bridge_id = models.AutoField(primary_key=True)
    song = models.ForeignKey('Song', models.SET_NULL, blank=True, null=True)
    artist = models.ForeignKey(Artist, models.SET_NULL, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'artist_song_bridge'
        app_label = 'albums'


class BuyerAccount(models.Model):
    buyer_id = models.AutoField(primary_key=True)
    postboard_name = models.CharField(max_length=64, blank=True, null=True)
    date_created = models.DateField()
    user = models.ForeignKey('User', models.SET_NULL, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'buyer_account'
        app_label = 'albums'


class Genre(models.Model):
    genre_id = models.AutoField(primary_key=True)
    genre_name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'genre'
        app_label = 'albums'


class SellerAccount(models.Model):
    seller_id = models.AutoField(primary_key=True)
    storefront_name = models.CharField(max_length=64, blank=True, null=True)
    date_created = models.DateField()
    user = models.ForeignKey('User', models.SET_NULL, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'seller_account'
        app_label = 'albums'


class Song(models.Model):
    song_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    length_minutes = models.SmallIntegerField()
    length_seconds = models.SmallIntegerField()
    song_lyrics = models.ForeignKey('SongLyrics', models.SET_NULL, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'song'
        app_label = 'albums'


class SongGenreBridge(models.Model):
    song_genre_bridge_id = models.AutoField(primary_key=True)
    song = models.ForeignKey(Song, models.SET_NULL, blank=True, null=True)
    genre = models.ForeignKey(Genre, models.SET_NULL, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'song_genre_bridge'
        app_label = 'albums'


class SongLyrics(models.Model):
    song_lyrics_id = models.AutoField(primary_key=True)
    lyrics = models.TextField()
    src_song = models.ForeignKey(Song, models.SET_NULL, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'song_lyrics'
        app_label = 'albums'


class ToBuyListing(models.Model):
    to_buy_listing_id = models.AutoField(primary_key=True)
    max_accepting_price = models.DecimalField(max_digits=65535, decimal_places=65535)
    date_posted = models.DateField(blank=True, null=True)
    album = models.ForeignKey(Album, models.SET_NULL, blank=True, null=True)
    buyer = models.ForeignKey(BuyerAccount, models.SET_NULL, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'to_buy_listing'
        app_label = 'albums'


class ToSellListing(models.Model):
    to_sell_listing_id = models.AutoField(primary_key=True)
    asking_price = models.DecimalField(max_digits=65535, decimal_places=65535)
    date_posted = models.DateField(blank=True, null=True)
    album = models.ForeignKey(Album, models.SET_NULL, blank=True, null=True)
    seller = models.ForeignKey(SellerAccount, models.SET_NULL, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'to_sell_listing'
        app_label = 'albums'


class User(models.Model):
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


class UserPassword(models.Model):
    password_id = models.AutoField(primary_key=True)
    encrypted_password = models.BinaryField()
    user = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_password'
        app_label = 'albums'

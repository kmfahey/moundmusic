# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

import os
import django

from django.db import models



class AlbumCovers(models.Model):
    album_cover_id = models.AutoField("album cover ID", primary_key=True)
    image_file_type = models.TextField("image file type")  # This field type is a guess.
    image_data = models.BinaryField("image data")
    album = models.ForeignKey('Albums', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = False
        db_table = 'album_covers'
        app_label = 'albums'


class Albums(models.Model):
    album_id = models.AutoField("album ID", primary_key=True)
    title = models.CharField("album title", max_length=256)
    number_of_discs = models.SmallIntegerField("number of discs")
    number_of_tracks = models.SmallIntegerField("number of tracks")
    release_date = models.DateField("release date", blank=True, null=True)
    album_cover = models.ForeignKey(AlbumCovers, blank=True, null=True, on_delete=models.SET_NULL)
    song_lyrics = models.ForeignKey('SongLyrics', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'albums'
        app_label = 'albums'


class AlbumsArtists(models.Model):
    albums_artists_id = models.AutoField(primary_key=True)
    album = models.ForeignKey(Albums, blank=True, null=True, on_delete=models.SET_NULL)
    artist = models.ForeignKey('Artists', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = False
        db_table = 'albums_artists'
        app_label = 'albums'


class AlbumsGenres(models.Model):
    albums_genres_id = models.AutoField(primary_key=True)
    album = models.ForeignKey(Albums, blank=True, null=True, on_delete=models.SET_NULL)
    genre = models.ForeignKey('Genres', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = False
        db_table = 'albums_genres'
        app_label = 'albums'


class AlbumsSongs(models.Model):
    albums_songs_id = models.AutoField(primary_key=True)
    album = models.ForeignKey(Albums, blank=True, null=True, on_delete=models.SET_NULL)
    disc_number = models.SmallIntegerField("disc number")
    track_number = models.SmallIntegerField("track number")
    song = models.ForeignKey('Songs', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = False
        db_table = 'albums_songs'
        app_label = 'albums'


class Artists(models.Model):
    artist_id = models.AutoField("artist ID", primary_key=True)
    first_name = models.CharField("first name", max_length=64)
    last_name = models.CharField("last name", max_length=64)
    gender = models.TextField()  # This field type is a guess.
    birth_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'artists'
        app_label = 'albums'


#class BuyerAccounts(models.Model):
#    buyer_id = models.AutoField("buyer ID", primary_key=True)
#    storefront_name = models.CharField("storefront name", max_length=64, blank=True, null=True)
#    date_created = models.DateField("date created")
#    user = models.ForeignKey('Users', blank=True, null=True, on_delete=models.SET_NULL)
#
#    class Meta:
#        managed = False
#        db_table = 'buyer_accounts'


class Genres(models.Model):
    genre_id = models.AutoField("genre ID", primary_key=True)
    genre_name = models.CharField("genre name", max_length=64)

    class Meta:
        managed = False
        db_table = 'genres'


#class SellerAccounts(models.Model):
#    seller_id = models.AutoField("seller ID", primary_key=True)
#    postboard_name = models.CharField("postboard name", max_length=64, blank=True, null=True)
#    date_created = models.DateField("date created")
#    user = models.ForeignKey('Users', blank=True, null=True, on_delete=models.SET_NULL)
#
#    class Meta:
#        managed = False
#        db_table = 'seller_accounts'


class SongLyrics(models.Model):
    song_lyrics_id = models.AutoField("Song lyrics ID", primary_key=True)
    lyrics = models.TextField("Song lyrics")
    song = models.ForeignKey('Songs', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'song_lyrics'
        app_label = 'albums'


class Songs(models.Model):
    song_id = models.AutoField("song ID", primary_key=True)
    title = models.CharField("song title", max_length=256)
    length_minutes = models.SmallIntegerField("song length minutes component")
    length_seconds = models.SmallIntegerField("song length seconds component")
    song_lyrics = models.ForeignKey(SongLyrics, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'songs'
        app_label = 'albums'


#class ToBuyListings(models.Model):
#    to_buy_listing_id = models.AutoField("to-buy listing ID", primary_key=True)
#    max_accepting_price = models.DecimalField("maximum price to accept", max_digits=65535, decimal_places=65535)
#    date_posted = models.DateField("date posted", blank=True, null=True)
#    album = models.ForeignKey(Albums, models.DO_NOTHING, blank=True, null=True)
#    buyer = models.ForeignKey(BuyerAccounts, models.DO_NOTHING, blank=True, null=True)
#
#    class Meta:
#        managed = False
#        db_table = 'to_buy_listings'


#class ToSellListings(models.Model):
#    to_sell_listing_id = models.AutoField("to-sell listing ID", primary_key=True)
#    asking_price = models.DecimalField("asking price", max_digits=65535, decimal_places=65535)
#    date_posted = models.DateField("date posted", blank=True, null=True)
#    album = models.ForeignKey(Albums, models.DO_NOTHING, blank=True, null=True)
#    seller = models.ForeignKey(SellerAccounts, models.DO_NOTHING, blank=True, null=True)
#
#    class Meta:
#        managed = False
#        db_table = 'to_sell_listings'


#class UserPasswords(models.Model):
#    password_id = models.AutoField("password ID", primary_key=True)
#    password_ciphertext = models.CharField("password ciphertext", max_length=256)
#    user = models.ForeignKey('Users', blank=True, null=True, on_delete=models.SET_NULL)
#
#    class Meta:
#        managed = False
#        db_table = 'user_passwords'


#class Users(models.Model):
#    user_id = models.AutoField("user ID", primary_key=True)
#    user_handle = models.CharField("user handle", max_length=16)
#    user_name = models.CharField("user name", max_length=64)
#    date_joined = models.DateField("date joined")
#    buyer_id = models.IntegerField(blank=True, null=True)
#    seller_id = models.IntegerField(blank=True, null=True)
#
#    class Meta:
#        managed = False
#        db_table = 'users'

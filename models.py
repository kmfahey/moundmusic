#!/usr/bin/python3

import django

from datetime import date
from django.db import models



class serializable(object):
    def serialize(self):
        return {column: getattr(self, column) for column in self.__columns__.keys()}

    @classmethod
    def validate_input(self, input_argd, all_nullable=False):
        validatedDict = dict()
        difference = set(input_argd.keys()) - set(self.__columns__)
        if difference:
            raise ValueError("unexpected key(s) in input: " + ', '.join(difference))
        for column, value in input_argd.items():
            column_type = self.__columns__[column]
            if value is None and not all_nullable and column not in self.__nullable_cols__:
                raise ValueError(f"value for {column} is null and column not nullable")
            elif column_type is int:
                try:
                    value = int(value)
                except ValueError:
                    raise ValueError(f"value for {column} isn't an integer: {value}")
                if value <= 0:
                    raise ValueError(f"value for {column} isn't greater than 0: {value}")
            elif column_type is float:
                try:
                    value = float(value)
                except ValueError:
                    raise ValueError(f"value for {column} isn't a decimal: {value}")
                if value <= 0:
                    raise ValueError(f"value for {column} isn't greater than 0: {value}")
            elif column_type is str and not len(value):
                raise ValueError(f"value for {column} is a string of zero length")
            elif column_type is date:
                try:
                    value = date.fromisoformat(value)
                except ValueError:
                    raise ValueError(f"value for {column} isn't in format YYYY-MM-DD and column is a DATE")
            elif isinstance(column_type, tuple):
                if value not in column_type:
                    enum_expr = ', '.join(f"'{option}'" for option in column_type[:-1]) + f" or '{column_type[-1]}'"
                    raise ValueError(f"value for {column} not one of {enum_expr} and column is an ENUM type")
            validatedDict[column] = value
        return validatedDict


class AbstractAlbum(models.Model, serializable):
    __columns__ = {'album_id':int, 'title':str, 'number_of_discs':int, 'number_of_tracks':int, 'release_date':date,
                   'album_cover_id':int}
    __nullable_cols__ = ('album_id', 'album_cover_id')

    album_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    number_of_discs = models.SmallIntegerField()
    number_of_tracks = models.SmallIntegerField()
    release_date = models.DateField(blank=True, null=True)
    album_cover = models.ForeignKey('AlbumCover', models.CASCADE, blank=True, null=True, related_name="+")

    class Meta:
        managed = False
        db_table = 'album'
        abstract = True


class AbstractAlbumCover(models.Model, serializable):
    __columns__ = {'album_cover_id':int, 'image_file_type':('png','jpg','gif'), 'image_data':bytes, 'album_id':int}
    __nullable_cols__ = ('album_cover_id', 'album_id')

    album_cover_id = models.AutoField(primary_key=True)
    # The column below is actually a ENUM('png', 'jpg', 'gif') postgresql custom
    # type, but django can't handle those. So long as it's only ever set to
    # (png|jpg|gif) there won't be any problems leaving it as a TextField.
    image_file_type = models.TextField()  # This field type is a guess.
    image_data = models.BinaryField()
    album = models.ForeignKey(Album, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'album_cover'
        abstract = True


class AbstractAlbumGenreBridge(models.Model):
    album_genre_bridge_id = models.AutoField(primary_key=True)
    album = models.ForeignKey(Album, models.CASCADE, blank=True, null=True)
    genre = models.ForeignKey('Genre', models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'album_genre_bridge'
        abstract = True


class AbstractAlbumSongBridge(models.Model):
    album_song_bridge_id = models.AutoField(primary_key=True)
    album = models.ForeignKey(Album, models.CASCADE, blank=True, null=True)
    disc_number = models.SmallIntegerField()
    track_number = models.SmallIntegerField()
    song = models.ForeignKey('Song', models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'album_song_bridge'
        abstract = True


class AbstractArtist(models.Model):
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
        abstract = True


class AbstractArtistAlbumBridge(models.Model):
    artist_album_bridge_id = models.AutoField(primary_key=True)
    album = models.ForeignKey(Album, models.CASCADE, blank=True, null=True)
    artist = models.ForeignKey(Artist, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'artist_album_bridge'
        abstract = True


class AbstractArtistGenreBridge(models.Model):
    artist_genre_bridge_id = models.AutoField(primary_key=True)
    artist = models.ForeignKey(Artist, models.CASCADE, blank=True, null=True)
    genre = models.ForeignKey('Genre', models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'artist_genre_bridge'
        abstract = True


class AbstractArtistSongBridge(models.Model):
    artist_song_bridge_id = models.AutoField(primary_key=True)
    song = models.ForeignKey('Song', models.CASCADE, blank=True, null=True)
    artist = models.ForeignKey(Artist, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'artist_song_bridge'
        abstract = True


class AbstractBuyerAccount(models.Model, serializable):
    __columns__ = {'buyer_id':int, 'postboard_name':str, 'date_created':date, 'user_id':int}
    __nullable_cols__ = ('buyer_id', 'user_id')

    buyer_id = models.AutoField(primary_key=True)
    postboard_name = models.CharField(max_length=64, blank=True, null=True)
    date_created = models.DateField()
    user = models.ForeignKey('User', models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'buyer_account'
        abstract = True


class AbstractGenre(models.Model, serializable):
    __columns__ = {'genre_id':int, 'genre_name':str}
    __nullable_cols__ = ('genre_id',)

    genre_id = models.AutoField(primary_key=True)
    genre_name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'genre'
        abstract = True


class AbstractSellerAccount(models.Model, serializable):
    __columns__ = {'seller_id':int, 'storefront_name':str, 'date_created':date, 'user_id':int}
    __nullable_cols__ = ('seller_id', 'user_id')

    seller_id = models.AutoField(primary_key=True)
    storefront_name = models.CharField(max_length=64, blank=True, null=True)
    date_created = models.DateField()
    user = models.ForeignKey('User', models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'seller_account'
        abstract = True


class AbstractSong(models.Model, serializable):
    __columns__ = {'song_id':int, 'title':str, 'length_minutes':int, 'length_seconds':int, 'song_lyrics_id':int}
    __nullable_cols__ = ('song_id', 'song_lyrics_id')

    song_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    length_minutes = models.SmallIntegerField()
    length_seconds = models.SmallIntegerField()
    song_lyrics = models.ForeignKey('SongLyrics', models.CASCADE, blank=True, null=True, related_name="+")

    class Meta:
        managed = False
        db_table = 'song'
        abstract = True


class AbstractSongGenreBridge(models.Model):
    song_genre_bridge_id = models.AutoField(primary_key=True)
    song = models.ForeignKey(Song, models.CASCADE, blank=True, null=True)
    genre = models.ForeignKey(Genre, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'song_genre_bridge'
        abstract = True


class AbstractSongLyrics(models.Model, serializable):
    __columns__ = {'song_lyrics_id':int, 'lyrics':str, 'song_id':int}
    __nullable_cols__ = ('song_lyrics_id', 'song_id')

    song_lyrics_id = models.AutoField(primary_key=True)
    lyrics = models.TextField()
    song = models.ForeignKey(Song, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'song_lyrics'
        abstract = True


class AbstractToBuyListing(models.Model, serializable):
    __columns__ = {'to_buy_listing_id':int, 'max_accepting_price':float, 'date_posted':date, 'album_id':int, 'buyer_id':int}
    __nullable_cols__ = ('to_buy_listing_id',)

    to_buy_listing_id = models.AutoField(primary_key=True)
    max_accepting_price = models.DecimalField(max_digits=65535, decimal_places=65535)
    date_posted = models.DateField(blank=True, null=True)
    album = models.ForeignKey(Album, models.CASCADE, blank=True, null=True)
    buyer = models.ForeignKey(BuyerAccount, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'to_buy_listing'
        abstract = True


class AbstractToSellListing(models.Model, serializable):
    __columns__ = {'to_sell_listing_id':int, 'asking_price':float, 'date_posted':date, 'album_id':int, 'seller_id':int}
    __nullable_cols__ = ('to_sell_listing_id',)

    to_sell_listing_id = models.AutoField(primary_key=True)
    asking_price = models.DecimalField(max_digits=65535, decimal_places=65535)
    date_posted = models.DateField(blank=True, null=True)
    album = models.ForeignKey(Album, models.CASCADE, blank=True, null=True)
    seller = models.ForeignKey(SellerAccount, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'to_sell_listing'
        abstract = True


class AbstractUser(models.Model, serializable):
    __columns__ = {'user_id':int, 'user_name':str, 'first_name':str, 'last_name':str,
                   'gender':('male','female','nonbinary'), 'date_joined':date, 'buyer_id':int, 'seller_id':int}
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
        abstract = True


class AbstractUserPassword(models.Model, serializable):
    __columns__ = {'password_id':int, 'encrypted_password':str, 'user_id':int}
    __nullable_cols__ = ('password_id', 'user_id')

    password_id = models.AutoField(primary_key=True)
    encrypted_password = models.BinaryField()
    user = models.ForeignKey(User, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_password'
        abstract = True

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Album(models.Model):
    album_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    number_of_discs = models.SmallIntegerField()
    number_of_tracks = models.SmallIntegerField()
    release_date = models.DateField(blank=True, null=True)
    album_cover = models.ForeignKey('AlbumCover', models.DO_NOTHING, blank=True, null=True)
    song_lyrics = models.ForeignKey('SongLyrics', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'album'


class AlbumCover(models.Model):
    album_cover_id = models.AutoField(primary_key=True)
    image_file_type = models.TextField()  # This field type is a guess.
    image_data = models.BinaryField()
    album = models.ForeignKey(Album, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'album_cover'


class AlbumGenreBridge(models.Model):
    albums_genres_id = models.AutoField(primary_key=True)
    album = models.ForeignKey(Album, models.DO_NOTHING, blank=True, null=True)
    genre = models.ForeignKey('Genre', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'album_genre_bridge'


class AlbumSongBridge(models.Model):
    albums_songs_id = models.AutoField(primary_key=True)
    album = models.ForeignKey(Album, models.DO_NOTHING, blank=True, null=True)
    disc_number = models.SmallIntegerField()
    track_number = models.SmallIntegerField()
    song = models.ForeignKey('Song', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'album_song_bridge'


class Artist(models.Model):
    artist_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    gender = models.TextField()  # This field type is a guess.
    birth_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'artist'


class ArtistAlbumBridge(models.Model):
    artists_albums_id = models.AutoField(primary_key=True)
    album = models.ForeignKey(Album, models.DO_NOTHING, blank=True, null=True)
    artist = models.ForeignKey(Artist, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'artist_album_bridge'


class ArtistGenreBridge(models.Model):
    artists_genres_id = models.AutoField(primary_key=True)
    artist = models.ForeignKey(Artist, models.DO_NOTHING, blank=True, null=True)
    genre = models.ForeignKey('Genre', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'artist_genre_bridge'


class ArtistSongBridge(models.Model):
    artists_songs_id = models.AutoField(primary_key=True)
    song = models.ForeignKey('Song', models.DO_NOTHING, blank=True, null=True)
    artist = models.ForeignKey(Artist, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'artist_song_bridge'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class BuyerAccount(models.Model):
    buyer_id = models.AutoField(primary_key=True)
    storefront_name = models.CharField(max_length=64, blank=True, null=True)
    date_created = models.DateField()
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'buyer_account'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Genre(models.Model):
    genre_id = models.AutoField(primary_key=True)
    genre_name = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'genre'


class SellerAccount(models.Model):
    seller_id = models.AutoField(primary_key=True)
    postboard_name = models.CharField(max_length=64, blank=True, null=True)
    date_created = models.DateField()
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'seller_account'


class Song(models.Model):
    song_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    length_minutes = models.SmallIntegerField()
    length_seconds = models.SmallIntegerField()
    song_lyrics = models.ForeignKey('SongLyrics', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'song'


class SongGenreBridge(models.Model):
    songs_genres_id = models.AutoField(primary_key=True)
    song = models.ForeignKey(Song, models.DO_NOTHING, blank=True, null=True)
    genre = models.ForeignKey(Genre, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'song_genre_bridge'


class SongLyrics(models.Model):
    song_lyrics_id = models.AutoField(primary_key=True)
    lyrics = models.TextField()
    song = models.ForeignKey(Song, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'song_lyrics'


class ToBuyListing(models.Model):
    to_buy_listing_id = models.AutoField(primary_key=True)
    max_accepting_price = models.DecimalField(max_digits=65535, decimal_places=65535)
    date_posted = models.DateField(blank=True, null=True)
    album = models.ForeignKey(Album, models.DO_NOTHING, blank=True, null=True)
    buyer = models.ForeignKey(BuyerAccount, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'to_buy_listing'


class ToSellListing(models.Model):
    to_sell_listing_id = models.AutoField(primary_key=True)
    asking_price = models.DecimalField(max_digits=65535, decimal_places=65535)
    date_posted = models.DateField(blank=True, null=True)
    album = models.ForeignKey(Album, models.DO_NOTHING, blank=True, null=True)
    seller = models.ForeignKey(SellerAccount, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'to_sell_listing'


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_handle = models.CharField(max_length=16)
    user_name = models.CharField(max_length=64)
    date_joined = models.DateField()
    buyer_id = models.IntegerField(blank=True, null=True)
    seller_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_'


class UserPassword(models.Model):
    password_id = models.AutoField(primary_key=True)
    password_ciphertext = models.CharField(max_length=256)
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_password'

# Generated by Django 3.2.15 on 2023-01-07 00:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AlbumCovers',
            fields=[
                ('album_cover_id', models.AutoField(primary_key=True, serialize=False, verbose_name='album cover ID')),
                ('image_file_type', models.TextField(verbose_name='image file type')),
                ('image_data', models.BinaryField(verbose_name='image data')),
            ],
            options={
                'db_table': 'album_covers',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Albums',
            fields=[
                ('album_id', models.AutoField(primary_key=True, serialize=False, verbose_name='album ID')),
                ('title', models.CharField(max_length=256, verbose_name='album title')),
                ('number_of_discs', models.SmallIntegerField(verbose_name='number of discs')),
                ('number_of_tracks', models.SmallIntegerField(verbose_name='number of tracks')),
                ('release_date', models.DateField(blank=True, null=True, verbose_name='release date')),
            ],
            options={
                'db_table': 'albums',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AlbumsArtists',
            fields=[
                ('albums_artists_id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'albums_artists',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AlbumsGenres',
            fields=[
                ('albums_genres_id', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'albums_genres',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AlbumsSongs',
            fields=[
                ('albums_songs_id', models.AutoField(primary_key=True, serialize=False)),
                ('disc_number', models.SmallIntegerField(verbose_name='disc number')),
                ('track_number', models.SmallIntegerField(verbose_name='track number')),
            ],
            options={
                'db_table': 'albums_songs',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Artists',
            fields=[
                ('artist_id', models.AutoField(primary_key=True, serialize=False, verbose_name='artist ID')),
                ('first_name', models.CharField(max_length=64, verbose_name='first name')),
                ('last_name', models.CharField(max_length=64, verbose_name='last name')),
                ('gender', models.TextField()),
                ('birth_date', models.DateField()),
            ],
            options={
                'db_table': 'artists',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Genres',
            fields=[
                ('genre_id', models.AutoField(primary_key=True, serialize=False, verbose_name='genre ID')),
                ('genre_name', models.CharField(max_length=64, verbose_name='genre name')),
            ],
            options={
                'db_table': 'genres',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SongLyrics',
            fields=[
                ('song_lyrics_id', models.AutoField(primary_key=True, serialize=False, verbose_name='Song lyrics ID')),
                ('lyrics', models.TextField(verbose_name='Song lyrics')),
            ],
            options={
                'db_table': 'song_lyrics',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Songs',
            fields=[
                ('song_id', models.AutoField(primary_key=True, serialize=False, verbose_name='song ID')),
                ('title', models.CharField(max_length=256, verbose_name='song title')),
                ('length_minutes', models.SmallIntegerField(verbose_name='song length minutes component')),
                ('length_seconds', models.SmallIntegerField(verbose_name='song length seconds component')),
            ],
            options={
                'db_table': 'songs',
                'managed': False,
            },
        ),
    ]
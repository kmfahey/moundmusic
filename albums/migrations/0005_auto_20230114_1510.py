# Generated by Django 3.2.15 on 2023-01-14 23:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('albums', '0004_auto_20230107_1930'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Album',
        ),
        migrations.DeleteModel(
            name='AlbumCover',
        ),
        migrations.DeleteModel(
            name='AlbumGenreBridge',
        ),
        migrations.DeleteModel(
            name='AlbumSongBridge',
        ),
        migrations.DeleteModel(
            name='Artist',
        ),
        migrations.DeleteModel(
            name='ArtistAlbumBridge',
        ),
        migrations.DeleteModel(
            name='ArtistGenreBridge',
        ),
        migrations.DeleteModel(
            name='ArtistSongBridge',
        ),
        migrations.DeleteModel(
            name='BuyerAccount',
        ),
        migrations.DeleteModel(
            name='Genre',
        ),
        migrations.DeleteModel(
            name='SellerAccount',
        ),
        migrations.DeleteModel(
            name='Song',
        ),
        migrations.DeleteModel(
            name='SongGenreBridge',
        ),
        migrations.DeleteModel(
            name='SongLyrics',
        ),
        migrations.DeleteModel(
            name='ToBuyListing',
        ),
        migrations.DeleteModel(
            name='ToSellListing',
        ),
        migrations.DeleteModel(
            name='User',
        ),
        migrations.DeleteModel(
            name='UserPassword',
        ),
    ]

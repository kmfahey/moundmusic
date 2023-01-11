#!/usr/bin/python3

from django.contrib import admin

from .models import AlbumCover
from .models import Album
from .models import AlbumGenreBridge
from .models import AlbumSongBridge
from .models import Artist
from .models import ArtistAlbumBridge
from .models import Genre
from .models import Song


admin.site.register(AlbumCover)
admin.site.register(Album)
admin.site.register(AlbumGenreBridge)
admin.site.register(AlbumSongBridge)
admin.site.register(Artist)
admin.site.register(ArtistAlbumBridge)
admin.site.register(Genre)
admin.site.register(Song)

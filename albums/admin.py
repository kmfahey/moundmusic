from django.contrib import admin

from .models import AlbumCovers
from .models import Albums
from .models import AlbumsArtists
from .models import AlbumsGenres
from .models import AlbumsSongs
from .models import Artists
from .models import SongLyrics
from .models import Songs

admin.site.register(AlbumCovers)
admin.site.register(Albums)
admin.site.register(AlbumsArtists)
admin.site.register(AlbumsGenres)
admin.site.register(AlbumsSongs)
admin.site.register(Artists)
admin.site.register(SongLyrics)
admin.site.register(Songs)


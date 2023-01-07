# moundmusic

This project is an exercise in building a REST API using django, completed as
part of the NuCamp coding bootcamp.

The goal for the project is to create a backend for a discography
website (akin to [discogs.com](https://discogs.com/) or
[musicbrainz.org](https://musicbrainz.org/)).

It will support display of artists, albums (with album covers), and songs
(with song lyrics). It will also track & display genres for artists, albums
and individual songs. It will support multiple artist authorship of an album,
individual per-song artist authorship for albums which source to "various
artists" (such as a soundtrack), and a song appearing on multiple albums.

It also will support a used CD buying-and-selling marketplace. A user of the
site will be able to register as a buyer or a seller (or both). Buyers will be
able to post wanted ads with maximum prices they'll pay, and sellers will be
able to maintain a storefront with listings for the CDs they're selling.

This is run with a postgresql database backend. The bulk of the project is
devoted to managing the REST APIs, and accessing or mutating data in the
database according to input from the API.

The frontend CMS sections this backend will support are:

1. album display
1. artist display
1. genre display,
1. song display
1. user profile page (private)
    1. a buyer interface (private)
    1. a seller interface (private)
1. buyer postboard page
1. seller storefront page

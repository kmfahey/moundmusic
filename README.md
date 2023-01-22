# moundmusic

This project is an exercise in building a REST API using django, completed as
part of the NuCamp coding bootcamp.

## Important

To run, this package needs two secrets files that were not included.
django will need its secret; create a file in the base directory named
'django\_secret\_key.dat' containing only that string. postgres needs its
username and password as well; create a file named 'postgres\_credentials.dat'
with the username on the first line and the password on the second.

## Background

This project provides a RESTful interface to a postgres database for
a discography website (akin to [discogs.com](https://discogs.com/) or
[musicbrainz.org](https://musicbrainz.org/)), complete with a used CD
marketplace akin to discogs.com's.

It supports creation, listing, modification and deletion of albums, artists,
songs and genres, as well as associating an object of any one of those four
types with objects of the remaining three, via the /albums, /songs, /genres,
/artists endpoints.

It also supports creation, listing, modification and deletion of user
accounts, as well as setting or authenticating passwords. Through the
/users/{userId}/buyer\_account and /users/{userId}/seller\_account endpoints,
it supports the creation, listing, modification and deletion of to-buy and
to-sell listings, as well as the creation, deletion and association of buyer
account and seller account objects with users.

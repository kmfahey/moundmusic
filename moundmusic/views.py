#!/usr/bin/python

from django.http.response import JsonResponse

from rest_framework import status
from rest_framework.decorators import api_view


endpoints_help = {
    "endpoints": {
        "site": {
            "/": {
                "GET": "Returns this help object."
            }
        },
        "albums": {
            "/albums": {
                "GET": "Returns a list of all albums.",
                "POST": "Adds the submitted object as a new album."
            },
            "/albums/{{albumId}}": {
                "GET": "Returns the album with id {{albumId}}.",
                "PATCH": "Updates the album with id {{albumId}} according to the data submitted.",
                "DELETE": "Deletes the album with id {{albumId}}."
            },
            "/albums/{{albumId}}/songs": {
                "GET": "Returns a list of all songs associated with the album with id {{albumId}}."
            },
            "/albums/{{albumId}}/songs/{{songId}}": {
                "GET": "Returns the song with id {{songId}} associated with the album with id {{albumId}}.",
                "DELETE": "Disassociates the song with id {{songId}} from the album with id {{albumId}}."
            },
            "/albums/{{albumId}}/genres": {
                "GET": "Returns a list of all genres associated with the album with id {{albumId}}.",
                "POST": "Accepts a {{genreId} and associates the genre with that id with the album with id {{albumId}}."
            },
            "/albums/{{albumId}}/genres/{{genreId}}": {
                "GET": "Returns the genre with id {{genreId}} associated with the album with id {{albumId}}.",
                "DELETE": "Disassociates the genre with id {{genreId}} from the album with id {{albumId}}."
            },
            "/albums/{{albumId}}/artists": {
                "GET": "Returns a list of all artists associated with the album with id {{albumId}}.",
                "POST": "Accepts an {{artistId}} and associates the artist with that id "
                        "with the album with id {{albumId}}."
            },
            "/albums/{{albumId}}/artists/{{artistId}}": {
                "GET": "Returns the artist with id {{artistId}} associated with the album with id {{albumId}}.",
                "DELETE": "Disassociates the artist with id {{artistId}} from the album with id {{albumId}}."
            },
        },
        "artists": {
            "/artists": {
                "GET": "Returns a list of all artists.",
                "POST": "Adds the submitted object as a new artist."
            },
            "/artists/{{artistId}}": {
                "GET": "Returns the artist with id {{artistId}}.",
                "PATCH": "Updates the artist with id {{artistId}} according to the data submitted.",
                "DELETE": "Deletes the artist with id {{artistId}}."
            },
            "/artists/{{artistId}}/songs": {
                "GET": "Returns a list of all songs associated with the artist with id {{artistId}}."
            },
            "/artists/{{artistId}}/songs/{{songId}}": {
                "GET": "Returns the song with id {{songId}} associated with the artist with id {{artistId}}.",
                "DELETE": "Disassociates the song with id {{songId}} from the artist with id {{artistId}}."
            },
            "/artists/{{artistId}}/genres": {
                "GET": "Returns a list of all genres associated with the artist with id {{artistId}}.",
                "POST": "Accepts a {{genreId}} and associates the genre with that id "
                        "with the artist with id {{artistId}}."
            },
            "/artists/{{artistId}}/genres/{{genreId}}": {
                "GET": "Returns the genre with id {{genreId}} associated with the artist with id {{artistId}}.",
                "DELETE": "Disassociates the genre with id {{genreId}} from the artist with id {{artistId}}."
            },
            "/artists/{{artistId}}/albums": {
                "GET": "Returns a list of all albums associated with the artist with id {{artistId}}.",
                "POST": "Accepts an {{albumId}} and associates the album with that id "
                        "with the artist with id {{artistId}}."
            },
            "/artists/{{artistId}}/albums/{{albumId}}": {
                "GET": "Returns the album with id {{albumId}} associated with the artist with id {{artistId}}.",
                "DELETE": "Disassociates the album with id {{albumId}} from the artist with id {{artistId}}."
            },
        },
        "genres": {
            "/genres": {
                "GET": "Returns a list of all genres.",
                "POST": "Adds the submitted object as a new genre."
            },
            "/genres/{{genreId}}": {
                "GET": "Returns the genre with id {{genreId}}.",
                "PATCH": "Updates the genre with id {{genreId}} according to the data submitted.",
                "DELETE": "Deletes the genre with id {{genreId}}."
            },
            "/genres/{{genreId}}/songs": {
                "GET": "Returns a list of all songs associated with the genre with id {{genreId}}."
            },
            "/genres/{{genreId}}/songs/{{songId}}": {
                "GET": "Returns the song with id {{songId}} associated with the genre with id {{genreId}}.",
                "DELETE": "Disassociates the song with id {{songId}} from the genre with id {{genreId}}."
            },
            "/genres/{{genreId}}/artists": {
                "GET": "Returns a list of all artists associated with the genre with id {{genreId}}.",
                "POST": "Accepts an {{artistId}} and associates the artist with that id "
                        "with the genre with id {{genreId}}."
            },
            "/genres/{{genreId}}/artists/{{artistId}}": {
                "GET": "Returns the artist with id {{artistId}} associated with the genre with id {{genreId}}.",
                "DELETE": "Disassociates the artist with id {{artistId}} from the genre with id {{genreId}}."
            },
            "/genres/{{genreId}}/albums": {
                "GET": "Returns a list of all albums associated with the genre with id {{genreId}}.",
                "POST": "Accepts an {{albumId}} and associates the album with that id "
                        "with the genre with id {{genreId}}."
            },
            "/genres/{{genreId}}/albums/{{albumId}}": {
                "GET": "Returns the album with id {{albumId}} associated with the genre with id {{genreId}}.",
                "DELETE": "Disassociates the album with id {{albumId}} from the genre with id {{genreId}}."
            },
        },
        "songs": {
            "/songs": {
                "GET": "Returns a list of all songs.",
                "POST": "Adds the submitted object as a new song."
            },
            "/songs/{{songId}}": {
                "GET": "Returns the song with id {{songId}}.",
                "PATCH": "Updates the song with id {{songId}} according to the data submitted.",
                "DELETE": "Deletes the song with id {{songId}}."
            },
            "/songs/{{songId}}/albums": {
                "GET": "Returns a list of all albums associated with the song with id {{songId}}."
            },
            "/songs/{{songId}}/albums/{{albumId}}": {
                "GET": "Returns the album with id {{albumId}} associated with the song with id {{songId}}.",
                "DELETE": "Disassociates the album with id {{albumId}} from the song with id {{songId}}."
            },
            "/songs/{{songId}}/artists": {
                "GET": "Returns a list of all artists associated with the song with id {{songId}}.",
                "POST": "Accepts an {{artistId}} and associates the artist "
                        "with that id with the song with id {{songId}}."
            },
            "/songs/{{songId}}/artists/{{artistId}}": {
                "GET": "Returns the artist with id {{artistId}} associated with the song with id {{songId}}.",
                "DELETE": "Disassociates the artist with id {{artistId}} from the song with id {{songId}}."
            },
            "/songs/{{songId}}/genres": {
                "GET": "Returns a list of all genres associated with the song with id {{songId}}.",
                "POST": "Accepts a {{genreId}} and associates the genre with that id with the song with id {{songId}}."
            },
            "/songs/{{songId}}/genres/{{genreId}}": {
                "GET": "Returns the genre with id {{genreId}} associated with the song with id {{songId}}.",
                "DELETE": "Disassociates the genre with id {{genreId}} from the song with id {{songId}}."
            },
            "/songs/{{songId}}/lyrics": {
                "GET": "Returns the song lyrics associated with the song with id {{songId}}.",
                "POST": "Adds the submitted object as new song lyrics associated with the song with id {{songId}}."
            },
            "/songs/{{songId}}/lyrics/{{lyricsId}}": {
                "GET": "Returns the song lyrics with id {{lyricsId}} associated with the song with id {{songId}}.",
                "DELETE": "Disassociates the song lyrics with id {{lyricsId}} from the song with id {{songId}}."
            },
        },
        "users": {
            "/users": {
                "GET": "Returns a list of all users.",
                "POST": "Adds the submitted object as a new user."
            },
            "/users/{{userId}}": {
                "GET": "Returns the user with id {{userId}}.",
                "PATCH": "Updates the user with id {{userId}} according to the data submitted.",
                "DELETE": "Deletes the user with id {{userId}}."
            },
            "/users/{{userId}}/password": {
                "POST": "Accepts a new password for the user with id {{userId}} and stores it."
            },
            "/users/{{userId}}/password/authenticate": {
                "POST": "Accepts a password and returns {'authenticates':true} if it authenticates against the stored "
                        "password for the user with id {{userId}}, or {'authenticates':false} if it does not."
            },
            "/users/{{userId}}/buyer_account": {
                "GET": "Returns the buyer account associated with the user with id {{userId}}.",
                "POST": "Accepts a {{buyerAccountId}} and associates the buyer account with that id "
                        "with the user with id {{userId}}."
            },
            "/users/{{userId}}/buyer_account/{{buyerAccountId}}": {
                "GET": "Returns the buyer account with id {{buyerAccountId}} associated "
                       "with the user with id {{userId}}.",
                "DELETE": "Disassociates the buyer account with id {{buyerAccountId}} from the user with id {{userId}}."
            },
            "/users/{{userId}}/buyer_account/{{buyerAccountId}}/listings": {
                "GET": "Returns the to-buy listings associated with the buyer account with that id associated "
                       "with the user with id {{userId}}.",
                "POST": "Adds the submitted object as a new to-buy listing associated with the buyer account "
                        "with id {{buyerAccountId}} associated with the user with id {{userId}}."
            },
            "/users/{{userId}}/buyer_account/{{buyerAccountId}}/listings/{{toBuyListingId}}": {
                "GET": "Returns the to-buy listing with id {{toBuyListingId}} associated with the buyer account "
                       "with id {{buyerAccountId}} associated with the user with id {{userId}}.",
                "PATCH": "Updates the to-buy listing with id {{toBuyListingId}} associated with the buyer account "
                         "with id {{buyerAccountId}} associated with the user with id {{userId}} according to the "
                         "data submitted.",
                "DELETE": "Deletes the to-buy listing with id {{toBuyListingId}} associated with the buyer account "
                          "listing with id {{toBuyListingId}} associated with the user with id {{userId}}."
            },
            "/users/{{userId}}/seller_account": {
                "GET": "Returns the seller account associated with the user with id {{userId}}.",
                "POST": "Accepts a {{sellerAccountId}} and associates the seller account "
                        "with that id with the user with id {{userId}}."
            },
            "/users/{{userId}}/seller_account/{{sellerAccountId}}": {
                "GET": "Returns the seller account with id {{sellerAccountId}} associated "
                       "with the user with id {{userId}}.",
                "DELETE": "Disassociates the seller account with id {{sellerAccountId}} from the user "
                          "with id {{userId}}."
            },
            "/users/{{userId}}/seller_account/{{sellerAccountId}}/listings": {
                "GET": "Returns the to-sell listings associated with the seller account with id "
                       "{{sellerAccountId}} associated with the user with id {{userId}}.",
                "POST": "Adds the submitted object as a new to-sell listing associated with the seller "
                        "account with id {{sellerAccountId}} associated with the user with id {{userId}}."
            },
            "/users/{{userId}}/seller_account/{{sellerAccountId}}/listings/{{toSellListingId}}": {
                "GET": "Returns the to-sell listing with id {{toSellListingId}} associated with the seller account "
                       "with id {{sellerAccountId}} associated with the user with id {{userId}}.",
                "PATCH": "Updates the to-sell listing with id {{toSellListingId}} associated with the seller account "
                         "with id {{sellerAccountId}} associated with the user with id {{userId}} according to the "
                         "data submitted.",
                "DELETE": "Deletes the to-sell listing with id {{toSellListingId}} associated with the seller account "
                          "with id {{sellerAccountId}} associated with the user with id {{userId}}."
            }
        }
    }
}


@api_view(['GET'])
def site_index(request):
    return JsonResponse(endpoints_help, status=status.HTTP_200_OK)

#!/usr/bin/python

from django.http.response import JsonResponse

from rest_framework import status
from rest_framework.decorators import api_view


endpoints_help = {
    "endpoints": {
        "site": {
            "/": {
                "GET": "returns this help object"
            }
        },
        "albums": {
            "/albums": {
                "GET": "returns a list of all albums.",
                "POST": "adds the submitted object as a new album."
            },
            "/albums/$ALBUMID": {
                "GET": "returns the album with that id.",
                "PATCH": "updates the album with that id according to the data submitted.",
                "DELETE": "deletes the album with that id."
            },
            "/albums/$ALBUMID/songs": {
                "GET": "returns a list of all songs associated with the album with that id."
            },
            "/albums/$ALBUMID/songs/$SONGID": {
                "GET": "returns the song with that id associated with the album with that id.",
                "DELETE": "disassociates the song with that id from the album with that id."
            },
            "/albums/$ALBUMID/genres": {
                "GET": "returns a list of all genres associated with the album with that id.",
                "POST": "accepts a genre id and associates the genre with that id with the album with that id."
            },
            "/albums/$ALBUMID/genres/$GENREID": {
                "GET": "returns the genre with that id associated with the album with that id.",
                "DELETE": "disassociates the genre with that id from the album with that id."
            },
            "/albums/$ALBUMID/artists": {
                "GET": "returns a list of all artists associated with the album with that id.",
                "POST": "accepts an artist id and associates the artist with that id with the album with that id."
            },
            "/albums/$ALBUMID/artists/$ARTISTID": {
                "GET": "returns the artist with that id associated with the album with that id.",
                "DELETE": "disassociates the artist with that id from the album with that id."
            },
        },
        "artists": {
            "/artists": {
                "GET": "returns a list of all artists.",
                "POST": "adds the submitted object as a new artist."
            },
            "/artists/$ARTISTID": {
                "GET": "returns the artist with that id.",
                "PATCH": "updates the artist with that id according to the data submitted.",
                "DELETE": "deletes the artist with that id."
            },
            "/artists/$ARTISTID/songs": {
                "GET": "returns a list of all songs associated with the artist with that id."
            },
            "/artists/$ARTISTID/songs/$SONGID": {
                "GET": "returns the song with that id associated with the artist with that id.",
                "DELETE": "disassociates the song with that id from the artist with that id."
            },
            "/artists/$ARTISTID/genres": {
                "GET": "returns a list of all genres associated with the artist with that id.",
                "POST": "accepts a genre id and associates the genre with that id with the artist with that id."
            },
            "/artists/$ARTISTID/genres/$GENREID": {
                "GET": "returns the genre with that id associated with the artist with that id.",
                "DELETE": "disassociates the genre with that id from the artist with that id."
            },
            "/artists/$ARTISTID/albums": {
                "GET": "returns a list of all albums associated with the artist with that id.",
                "POST": "accepts an album id and associates the album with that id with the artist with that id."
            },
            "/artists/$ARTISTID/albums/$ALBUMID": {
                "GET": "returns the album with that id associated with the artist with that id.",
                "DELETE": "disassociates the album with that id from the artist with that id."
            },
        },
        "genres": {
            "/genres": {
                "GET": "returns a list of all genres.",
                "POST": "adds the submitted object as a new genre."
            },
            "/genres/$GENREID": {
                "GET": "returns the genre with that id.",
                "PATCH": "updates the genre with that id according to the data submitted.",
                "DELETE": "deletes the genre with that id."
            },
            "/genres/$GENREID/songs": {
                "GET": "returns a list of all songs associated with the genre with that id."
            },
            "/genres/$GENREID/songs/$SONGID": {
                "GET": "returns the song with that id associated with the genre with that id.",
                "DELETE": "disassociates the song with that id from the genre with that id."
            },
            "/genres/$GENREID/artists": {
                "GET": "returns a list of all artists associated with the genre with that id.",
                "POST": "accepts a artist id and associates the artist with that id with the genre with that id."
            },
            "/genres/$GENREID/artists/$ARTISTID": {
                "GET": "returns the artist with that id associated with the genre with that id.",
                "DELETE": "disassociates the artist with that id from the genre with that id."
            },
            "/genres/$GENREID/albums": {
                "GET": "returns a list of all albums associated with the genre with that id.",
                "POST": "accepts an album id and associates the album with that id with the genre with that id."
            },
            "/genres/$GENREID/albums/$ALBUMID": {
                "GET": "returns the album with that id associated with the genre with that id.",
                "DELETE": "disassociates the album with that id from the genre with that id."
            },
        },
        "songs": {
            "/songs": {
                "GET": "returns a list of all songs.",
                "POST": "adds the submitted object as a new song."
            },
            "/songs/$SONGID": {
                "GET": "returns the song with that id.",
                "PATCH": "updates the song with that id according to the data submitted.",
                "DELETE": "deletes the song with that id."
            },
            "/songs/$SONGID/albums": {
                "GET": "returns a list of all genres associated with the song with that id."
            },
            "/songs/$SONGID/albums/$ALBUMID": {
                "GET": "returns the genre with that id associated with the song with that id.",
                "DELETE": "disassociates the genre with that id from the song with that id."
            },
            "/songs/$SONGID/artists": {
                "GET": "returns a list of all artists associated with the song with that id.",
                "POST": "accepts a artist id and associates the artist with that id with the song with that id."
            },
            "/songs/$SONGID/artists/$ARTISTID": {
                "GET": "returns the artist with that id associated with the song with that id.",
                "DELETE": "disassociates the artist with that id from the song with that id."
            },
            "/songs/$SONGID/genres": {
                "GET": "returns a list of all albums associated with the song with that id.",
                "POST": "accepts an album id and associates the album with that id with the song with that id."
            },
            "/songs/$SONGID/genres/$GENREID": {
                "GET": "returns the album with that id associated with the song with that id.",
                "DELETE": "disassociates the album with that id from the song with that id."
            },
            "/songs/$SONGID/lyrics": {
                "GET": "returns the lyrics associated with the song with that id.",
                "POST": "accepts a song lyrics id and associates the lyrics with that id with the song with that id."
            },
            "/songs/$SONGID/lyrics/$LYRICSID": {
                "GET": "returns the lyrics with that id associated with the song with that id.",
                "DELETE": "disassociates the lyrics with that id from the song with that id."
            },
        },
        "users": {
            "/users": {
                "GET": "returns a list of all users.",
                "POST": "adds the submitted object as a new user."
            },
            "/users/$USERID": {
                "GET": "returns the user with that id.",
                "PATCH": "updates the user with that id according to the data submitted.",
                "DELETE": "deletes the user with that id."
            },
            "/users/$USERID/password": {
                "POST": "accepts a new password and stores it."
            },
            "/users/$USERID/password/authenticate": {
                "POST": "accepts a password and returns {'authenticates':true} if it authenticates against the stored "
                        "password for the user with that id, or {'authenticates':false} if it does not."
            },
            "/users/$USERID/buyer_account": {
                "GET": "returns the buyer account associated with the user with that id.",
                "POST": "accepts a buyer account id and associates it with the user with that id."
            },
            "/users/$USERID/buyer_account/$ACCOUNTID": {
                "GET": "returns the buyer account with that id associated with the user with that id.",
                "DELETE": "disassociates the buyer account with that id from the user with that id."
            },
            "/users/$USERID/buyer_account/$ACCOUNTID/listings": {
                "GET": "returns the to-buy listings associated with the buyer account with that id associated with the user "
                       "with that id.",
                "POST": "adds the submitted object as a new to-buy listing associated with the buyer account with that id "
                        "associated with the user with that id."
            },
            "/users/$USERID/buyer_account/$ACCOUNTID/listings/$LISTINGID": {
                "GET": "returns the to-buy listing with that id associated with the buyer account with that id associated "
                       "with the user with that id.",
                "PATCH": "updates the to-buy listing with that id associated with the buyer account with that id "
                         "associated with the user with that id according to the data submitted.",
                "DELETE": "deletes the to-buy listing with that id associated with the buyer account listing with that id "
                          "associated with the user with that id."
            },
            "/users/$USERID/seller_account": {
                "GET": "returns the buyer account associated with the user with that id.",
                "POST": "accepts a buyer account id and associates it with the user with that id."
            },
            "/users/$USERID/seller_account/$ACCOUNTID": {
                "GET": "returns the buyer account with that id associated with the user with that id.",
                "DELETE": "disassociates the buyer account with that id from the user with that id."
            },
            "/users/$USERID/seller_account/$ACCOUNTID/listings": {
                "GET": "returns the to-buy listings associated with the buyer account with that id associated with the "
                       "user with that id.",
                "POST": "adds the submitted object as a new to-buy listing associated with the buyer account with that id "
                        "associated with the user with that id."
            },
            "/users/$USERID/seller_account/$ACCOUNTID/listings/$LISTINGID": {
                "GET": "returns the to-buy listing with that id associated with the buyer account with that id associated "
                       "with the user with that id.\n",
                "PATCH": "updates the to-buy listing with that id associated with the buyer account with that id "
                         "associated with the user with that id according to the data submitted.\n",
                "DELETE": "deletes the to-buy listing with that id associated with the buyer account listing with that id "
                          "associated with the user with that id."
            }
        }
    }
}


@api_view(['GET'])
def site_index(request):
    return JsonResponse(endpoints_help, status=status.HTTP_200_OK)

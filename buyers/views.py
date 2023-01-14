#!/usr/bin/python

from django.shortcuts import render

from albums.models import BuyerAccount, ToBuyListing



## GET,POST          /artists
#index = define_GET_POST_index_closure(BuyerAccount, 'buyer_id')
#
#
### GET,PATCH,DELETE  /buyers/<buyer_id>
#single_buyer = define_single_model_GET_PATCH_DELETE_closure(BuyerAccount, 'buyer_id')
#
#
## GET,POST         /buyers/<buyer_id>/to_buy_listings
#single_buyer_to_buy_listings = # custom
#
#
## GET,PATCH,DELETE /buyers/<buyer_id>/to_buy_listings/<to_buy_listing_id>
#single_buyer_single_to_buy_listing = # custom
#
#

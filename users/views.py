#!/usr/bin/python

import bcrypt

from datetime import date

from json import loads as json_loads, JSONDecodeError

from django.http.response import JsonResponse
from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework import status

from moundmusic.viewutils import dispatch_funcs_by_method, validate_post_request, validate_input
from moundmusic.viewutils import define_GET_POST_index_closure, define_single_model_GET_PATCH_DELETE_closure, \
        define_single_user_single_buyer_or_seller_account_single_listing_GET_PATCH_DELETE_closure, \
        define_single_user_single_buyer_or_seller_account_any_listing_GET_POST_closure, \
        define_single_user_single_buyer_or_seller_account_GET_DELETE_closure, \
        define_single_user_any_buyer_or_seller_account_GET_POST_closure

from .models import User, UserPassword, BuyerAccount, SellerAccount, ToBuyListing, ToSellListing


def validate_user_password_input(request, user_id):
    try:
        User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'message': f'no user with user_id={user_id}'},
                            status=status.HTTP_404_NOT_FOUND)
    try:
        json_content = json_loads(request.body)
    except JSONDecodeError:
        return JsonResponse({'message': 'JSON did not parse'}, status=status.HTTP_400_BAD_REQUEST)
    keys_found = set(json_content.keys())
    keys_found.remove('password')
    if keys_found:
        prop_expr = ', '.join(f"'{property}'" for property in keys_found)
        return JsonResponse({'message': f'unexpected propert{"ies" if len(keys_found) > 1 else "y"} '
                                        f'in input: {prop_expr}'},
                            status=status.HTTP_400_BAD_REQUEST)
    return json_content



# GET,POST          /users
index = define_GET_POST_index_closure(User, 'user_id')


# GET,PATCH,DELETE  /users/<user_id>
single_user = define_single_model_GET_PATCH_DELETE_closure(User, 'user_id')


# POST          /users/<user_id>/password
@api_view(['POST'])
def single_user_password_set_password(request, model_obj_id):
    result = validate_user_password_input(request, model_obj_id)
    if isinstance(result, JsonResponse):
        return result
    json_content = result
    password = json_content['password'].encode("utf8")
    salt = bcrypt.gensalt()
    encrypted_password = bcrypt.hashpw(password, salt)
    try:
        user_password = UserPassword.objects.get(user_id=model_obj_id)
    except UserPassword.DoesNotExist:
        max_password_id = max(user_password.password_id for user_password in UserPassword.objects.filter())
        user_password = UserPassword(password_id=max_password_id + 1, encrypted_password=encrypted_password,
                                     user_id=model_obj_id)
    else:
        user_password.encrypted_password = encrypted_password
    user_password.save()
    return JsonResponse(user_password.serialize(), status=status.HTTP_200_OK, safe=False)


## POST             /users/<user_id>/password/authenticate
@api_view(['POST'])
def single_user_password_authenticate(request, model_obj_id):
    result = validate_user_password_input(request, model_obj_id)
    if isinstance(result, JsonResponse):
        return result
    json_content = result
    try:
        user_password = UserPassword.objects.get(user_id=model_obj_id)
    except UserPassword.DoesNotExist:
        return JsonResponse({'message': f'user with user_id={model_obj_id} has no password set'},
                            status=status.HTTP_404_NOT_FOUND)
    password_tocheck = json_content['password'].encode("utf-8")
    salt = bcrypt.gensalt()
    password_onrecord_enc = bytes(user_password.encrypted_password)
    outcome = bcrypt.checkpw(password_tocheck, password_onrecord_enc)
    return JsonResponse({'authenticates': outcome}, status=status.HTTP_200_OK, safe=False)


# GET,POST          /users/<ID>/buyer_account
single_user_any_buyer_account = define_single_user_any_buyer_or_seller_account_GET_POST_closure(BuyerAccount, 'buyer_id')


# GET,DELETE        /users/<ID>/buyer_account/<ID>
single_user_single_buyer_account = define_single_user_single_buyer_or_seller_account_GET_DELETE_closure(BuyerAccount, 'buyer_id')


# GET,POST          /users/<ID>/seller_account
single_user_any_seller_account = define_single_user_any_buyer_or_seller_account_GET_POST_closure(SellerAccount, 'seller_id')


# GET,DELETE        /users/<ID>/seller_account/<ID>
single_user_single_seller_account = define_single_user_single_buyer_or_seller_account_GET_DELETE_closure(SellerAccount,
'seller_id')


# GET,POST          /users/<ID>/seller_account/<ID>/listings
single_user_single_buyer_account_any_listing = define_single_user_single_buyer_or_seller_account_any_listing_GET_POST_closure(
                                                   BuyerAccount, 'buyer_id', ToBuyListing)


# GET,DELETE       /users/<ID>/seller_account/<ID>/listings/<ID>
single_user_single_buyer_account_single_listing = define_single_user_single_buyer_or_seller_account_single_listing_GET_PATCH_DELETE_closure(
                                                      BuyerAccount, 'buyer_id', ToBuyListing, 'to_buy_listing_id')


# GET,POST          /users/<ID>/seller_account/<ID>/listings
single_user_single_seller_account_any_listing = define_single_user_single_buyer_or_seller_account_any_listing_GET_POST_closure(
                                                    SellerAccount, 'seller_id', ToSellListing)


# GET,DELETE       /users/<ID>/seller_account/<ID>/listings/<ID>
single_user_single_seller_account_single_listing = define_single_user_single_buyer_or_seller_account_single_listing_GET_PATCH_DELETE_closure(
                                                       SellerAccount, 'seller_id', ToSellListing, 'to_sell_listing_id')

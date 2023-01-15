#!/usr/bin/python

import bcrypt

from datetime import date

from json import loads as json_loads, JSONDecodeError

from django.http.response import JsonResponse
from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework import status

from moundmusic.viewutils import  dispatch_funcs_by_method, validate_post_request, \
        validate_bridged_table_column_value_pair, validate_input
from moundmusic.viewutils import define_GET_POST_index_closure, define_single_model_GET_PATCH_DELETE_closure, \
        define_single_outer_model_all_of_inner_model_GET_POST_closure, \
        define_single_outer_model_single_inner_model_GET_DELETE_closure

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
        return JsonResponse({'message':'JSON did not parse'}, status=status.HTTP_400_BAD_REQUEST)
    keys_found = set(json_content.keys())
    keys_found.remove('password')
    if keys_found:
        prop_expr = ', '.join(f"'{property}'" for property in keys_found)
        return JsonResponse({'message': f'unexpected propert{"ies" if len(keys_found) > 1 else "y"} '
                                        f'in input: {prop_expr}'},
                            status=status.HTTP_400_BAD_REQUEST)
    return json_content


def define_single_user_any_buyer_or_seller_account_closure(buyer_or_seller_account_class, buyer_or_seller_id_col_name):
    @api_view(['GET', 'POST'])
    def single_user_any_buyer_or_seller_account(request, outer_model_obj_id):
        def _single_user_any_buyer_or_seller_account_GET():
            try:
                user = User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse({'message': f'no user with user_id={outer_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            if getattr(user, buyer_or_seller_id_col_name) is None:
                return JsonResponse({"message":f"user with user_id={outer_model_obj_id} has "
                                                "no associated buyer account"},
                                    content_type="application/json", status=status.HTTP_404_NOT_FOUND)
            buyer_account = buyer_or_seller_account_class.objects.get(user_id=outer_model_obj_id)
            return JsonResponse(buyer_account.serialize(), status=status.HTTP_200_OK, safe=False)

        def _single_user_any_buyer_or_seller_account_POST():
            try:
                user = User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse({'message': f'no user with user_id={outer_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            buyer_or_seller_id = getattr(user, buyer_or_seller_id_col_name)
            kind_of_account = buyer_or_seller_id_col_name.split('_')[0]
            if buyer_or_seller_id is not None:
                return JsonResponse({"message":f"user with user_id={outer_model_obj_id} already has "
                                               f"a {kind_of_account} account with "
                                               f"{buyer_or_seller_id_col_name}={buyer_or_seller_id} associated"},
                                    content_type="application/json", status=status.HTTP_404_NOT_FOUND)
            result = validate_post_request(request, buyer_or_seller_account_class)
            if isinstance(result, JsonResponse):
                return result
            json_content = result
            keys_found = set(json_content.keys())
            if buyer_or_seller_account_class is BuyerAccount:
                keys_found.remove('postboard_name')
            else:
                keys_found.remove('storefront_name')
            if keys_found:
                prop_expr = ', '.join(f"'{property}'" for property in keys_found)
                return JsonResponse({'message': f'unexpected propert{"ies" if len(keys_found) > 1 else "y"} '
                                                f'in input: {prop_expr}'},
                                    status=status.HTTP_400_BAD_REQUEST)
            json_content['date_created'] = date.today()
            json_content['user_id'] = user.user_id
            buyer_or_seller_account = buyer_or_seller_account_class(**json_content)
            buyer_or_seller_account.user_id = user.user_id
            buyer_or_seller_account.save()
            setattr(user, buyer_or_seller_id_col_name, getattr(buyer_or_seller_account, buyer_or_seller_id_col_name))
            user.save()
            return JsonResponse(buyer_or_seller_account.serialize(), status=status.HTTP_200_OK)

        return dispatch_funcs_by_method((_single_user_any_buyer_or_seller_account_GET,
                                          _single_user_any_buyer_or_seller_account_POST), request)

    return single_user_any_buyer_or_seller_account


def define_single_user_single_buyer_or_seller_account_closure(buyer_or_seller_account_class,
                                                              buyer_or_seller_id_col_name):

    @api_view(['GET', 'DELETE'])
    def single_user_single_buyer_or_seller_account(request, outer_model_obj_id, inner_model_obj_id):
        def _single_user_single_buyer_or_seller_account_GET():
            try:
                user = User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse({'message': f'no user with user_id={outer_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            try:
                buyer_or_seller_account = buyer_or_seller_account_class.objects.get(
                                              **{buyer_or_seller_id_col_name: inner_model_obj_id})
            except buyer_or_seller_account_class.DoesNotExist:
                return JsonResponse({'message': f"no buyer account with "
                                                f"{buyer_or_seller_id_col_name}={outer_model_obj_id}"},
                                    status=status.HTTP_404_NOT_FOUND)
            return JsonResponse(buyer_or_seller_account.serialize(), status=status.HTTP_200_OK, safe=False)

        def _single_user_single_buyer_or_seller_account_DELETE():
            try:
                user = User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse({'message': f'no user with user_id={outer_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            try:
                buyer_or_seller_account = buyer_or_seller_account_class.objects.get(
                                              **{buyer_or_seller_id_col_name: inner_model_obj_id})
            except buyer_or_seller_account_class.DoesNotExist:
                return JsonResponse({'message': f'no buyer accout with '
                                                f'{buyer_or_seller_id_col_name}={outer_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            setattr(user, buyer_or_seller_id_col_name, None)
            user.save()
            kind_of_account = buyer_or_seller_id_col_name.split('_')[0]
            buyer_or_seller_account.delete()
            return JsonResponse({"message":f"{kind_of_account} account with "
                                           f"{buyer_or_seller_id_col_name}={inner_model_obj_id} associated with "
                                           f"user with user_id={outer_model_obj_id} disassociated and deleted"},
                                status=status.HTTP_200_OK)

        return dispatch_funcs_by_method((_single_user_single_buyer_or_seller_account_GET,
                                         _single_user_single_buyer_or_seller_account_DELETE), request)

    return single_user_single_buyer_or_seller_account


def define_single_user_single_buyer_or_seller_account_any_listing_closure(buyer_or_seller_class,
                                                                          buyer_or_seller_id_col_name,
                                                                          to_buy_or_to_sell_listing_class):

    @api_view(['GET', 'POST'])
    def single_user_single_buyer_or_seller_account_any_listing(request, outer_model_obj_id, inner_model_obj_id):
        def _single_user_single_buyer_or_seller_account_any_listing_GET():
            try:
                user = User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse({'message': f'no user with user_id={outer_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            kind_of_account = buyer_or_seller_id_col_name.split('_')[0]
            try:
                buyer_or_seller_account = buyer_or_seller_class.objects.get(
                                              **{buyer_or_seller_id_col_name: inner_model_obj_id})
            except buyer_or_seller_class.DoesNotExist:
                return JsonResponse({'message': f'no {kind_of_account} account with '
                                                f'{buyer_or_seller_id_col_name}={inner_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            listings = to_buy_or_to_sell_listing_class.objects.filter(
                           **{buyer_or_seller_id_col_name: inner_model_obj_id})
            listings_serialized = [listing.serialize() for listing in listings]
            return JsonResponse(listings_serialized, status=status.HTTP_200_OK, safe=False)

        def _single_user_single_buyer_or_seller_account_any_listing_POST():
            try:
                user = User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse({'message': f'no user with user_id={outer_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            kind_of_account = buyer_or_seller_id_col_name.split('_')[0]
            try:
                buyer_or_seller_account = buyer_or_seller_class.objects.get(
                                              **{buyer_or_seller_id_col_name: inner_model_obj_id})
            except buyer_or_seller_class.DoesNotExist:
                return JsonResponse({'message': f'no {kind_of_account} account with '
                                                f'{buyer_or_seller_id_col_name}={inner_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            try:
                json_content = json_loads(request.body)
            except JSONDecodeError:
                return JsonResponse({'message':'JSON did not parse'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                json_content = validate_input(to_buy_or_to_sell_listing_class, json_content, all_nullable=True)
            except ValueError as exception:
                return JsonResponse({'message':exception.args[0]}, status=status.HTTP_400_BAD_REQUEST)
            if buyer_or_seller_class is BuyerAccount:
                keys_required = set(("max_accepting_price", "album_id"))
            else:
                keys_required = set(("asking_price", "album_id"))
            keys_found = set(json_content.keys())
            diff = keys_required - keys_found
            if diff:
                prop_expr = ', '.join(f"'{property}'" for property in diff)
                return JsonResponse({'message': f'json object missing required '
                                                f'propert{"ies" if len(diff) > 1 else "y"}: {prop_expr}'},
                                    status=status.HTTP_400_BAD_REQUEST)
            diff = keys_found - keys_required
            if diff:
                prop_expr = ', '.join(f"'{property}'" for property in diff)
                return JsonResponse({'message': f'unexpected propert{"ies" if len(diff) > 1 else "y"} '
                                                f'in input: {prop_expr}'},
                                    status=status.HTTP_400_BAD_REQUEST)
            json_content['date_posted'] = date.today()
            listing = to_buy_or_to_sell_listing_class(**json_content)
            setattr(listing, buyer_or_seller_id_col_name, getattr(buyer_or_seller_account, buyer_or_seller_id_col_name))
            listing.save()
            return JsonResponse(listing.serialize(), status=status.HTTP_200_OK)

        return dispatch_funcs_by_method((_single_user_single_buyer_or_seller_account_any_listing_GET,
                                         _single_user_single_buyer_or_seller_account_any_listing_POST), request)

    return single_user_single_buyer_or_seller_account_any_listing


def define_single_user_single_buyer_or_seller_account_single_listing_closure(buyer_or_seller_class,
                                                                             buyer_or_seller_id_col_name,
                                                                             to_buy_or_to_sell_listing_class,
                                                                             to_buy_or_to_sell_listing_id_col_name):
    @api_view(['GET', 'DELETE'])
    def single_user_single_buyer_or_seller_account_single_listing(request, outer_model_obj_id, inner_model_obj_id,
                                                                  third_model_obj_id):

        def _single_user_single_buyer_or_seller_account_single_listing_GET():
            try:
                user = User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse({'message': f'no user with user_id={outer_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            kind_of_account = buyer_or_seller_id_col_name.split('_')[0]
            try:
                buyer_or_seller_account = buyer_or_seller_class.objects.get(
                                              **{buyer_or_seller_id_col_name: inner_model_obj_id})
            except buyer_or_seller_class.DoesNotExist:
                return JsonResponse({'message': f'no {kind_of_account} account with '
                                                f'{buyer_or_seller_id_col_name}={inner_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            kind_of_listing = "to-buy listing" if buyer_or_seller_class is BuyerAccount else "to-sell listing"
            try:
                listing = to_buy_or_to_sell_listing_class.objects.get(
                              **{to_buy_or_to_sell_listing_id_col_name: third_model_obj_id})
            except to_buy_or_to_sell_listing_class.DoesNotExist:
                return JsonResponse({'message': f'no {kind_of_listing} with '
                                                f'{to_buy_or_to_sell_listing_id_col_name}={third_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            return JsonResponse(listing.serialize(), status=status.HTTP_200_OK, safe=False)

        def _single_user_single_buyer_or_seller_account_single_listing_DELETE():
            try:
                user = User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse({'message': f'no user with user_id={outer_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            kind_of_account = buyer_or_seller_id_col_name.split('_')[0]
            try:
                buyer_or_seller_account = buyer_or_seller_class.objects.get(
                                              **{buyer_or_seller_id_col_name: inner_model_obj_id})
            except buyer_or_seller_class.DoesNotExist:
                return JsonResponse({'message': f'no {kind_of_account} account with '
                                                f'{buyer_or_seller_id_col_name}={inner_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            kind_of_listing = "to-buy listing" if buyer_or_seller_class is BuyerAccount else "to-sell listing"
            try:
                listing = to_buy_or_to_sell_listing_class.objects.get(
                              **{to_buy_or_to_sell_listing_id_col_name: third_model_obj_id})
            except to_buy_or_to_sell_listing_class.DoesNotExist:
                return JsonResponse({'message': f'no {kind_of_listing} with '
                                                f'{to_buy_or_to_sell_listing_id_col_name}={third_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            listing.delete()
            return JsonResponse({"message":f"{kind_of_listing} with "
                                           f"{to_buy_or_to_sell_listing_id_col_name}={third_model_obj_id} deleted"},
                                status=status.HTTP_200_OK)

        return dispatch_funcs_by_method((_single_user_single_buyer_or_seller_account_single_listing_GET,
                                         _single_user_single_buyer_or_seller_account_single_listing_DELETE), request)

    return single_user_single_buyer_or_seller_account_single_listing


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
        user_password = UserPassword(encrypted_password=encrypted_password)
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
        return JsonResponse({'message':f'user with user_id={model_obj_id} has no password set'},
                            status=status.HTTP_404_NOT_FOUND)
    password_tocheck = json_content['password'].encode("utf-8")
    salt = bcrypt.gensalt()
    password_onrecord_enc = bytes(user_password.encrypted_password)
    outcome = bcrypt.checkpw(password_tocheck, password_onrecord_enc)
    return JsonResponse({'authenticates':outcome}, status=status.HTTP_200_OK, safe=False)


# GET,POST          /users/<ID>/buyer_account
single_user_any_buyer_account = define_single_user_any_buyer_or_seller_account_closure(BuyerAccount, 'buyer_id')


# GET,DELETE        /users/<ID>/buyer_account/<ID>
single_user_single_buyer_account = define_single_user_single_buyer_or_seller_account_closure(BuyerAccount, 'buyer_id')


# GET,POST          /users/<ID>/seller_account
single_user_any_seller_account = define_single_user_any_buyer_or_seller_account_closure(SellerAccount, 'seller_id')


# GET,DELETE        /users/<ID>/seller_account/<ID>
single_user_single_seller_account = define_single_user_single_buyer_or_seller_account_closure(SellerAccount,
'seller_id')


# GET,POST          /users/<ID>/seller_account/<ID>/listings
single_user_single_buyer_account_any_listing = define_single_user_single_buyer_or_seller_account_any_listing_closure(
                                                   BuyerAccount, 'buyer_id', ToBuyListing)


# GET,DELETE       /users/<ID>/seller_account/<ID>/listings/<ID>
single_user_single_buyer_account_single_listing = define_single_user_single_buyer_or_seller_account_single_listing_closure(
                                                      BuyerAccount, 'buyer_id', ToBuyListing, 'to_buy_listing_id')


# GET,POST          /users/<ID>/seller_account/<ID>/listings
single_user_single_seller_account_any_listing = define_single_user_single_buyer_or_seller_account_any_listing_closure(
                                                    SellerAccount, 'seller_id', ToSellListing)


# GET,DELETE       /users/<ID>/seller_account/<ID>/listings/<ID>
single_user_single_seller_account_single_listing = define_single_user_single_buyer_or_seller_account_single_listing_closure(
                                                       SellerAccount, 'seller_id', ToSellListing, 'to_sell_listing_id')

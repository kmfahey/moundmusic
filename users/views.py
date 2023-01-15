#!/usr/bin/python

import bcrypt

from datetime import date

from json import loads as json_loads, JSONDecodeError

from django.http.response import JsonResponse
from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework import status

from moundmusic.viewutils import  dispatch_funcs_by_method, validate_post_request, \
        validate_bridged_table_column_value_pair
from moundmusic.viewutils import define_GET_POST_index_closure, define_single_model_GET_PATCH_DELETE_closure, \
        define_single_outer_model_all_of_inner_model_GET_POST_closure, \
        define_single_outer_model_single_inner_model_GET_DELETE_closure

from .models import User, UserPassword, BuyerAccount, SellerAccount


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
                return JsonResponse({"message":f"user with user_id={outer_model_obj_id} has no associated buyer account"},
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


def define_single_user_single_buyer_or_seller_account_closure(buyer_or_seller_account_class, buyer_or_seller_id_col_name):

    @api_view(['GET', 'DELETE'])
    def single_user_single_buyer_or_seller_account(request, outer_model_obj_id, inner_model_obj_id):
        def _single_user_single_buyer_or_seller_account_GET():
            try:
                user = User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse({'message': f'no user with user_id={outer_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            try:
                buyer_or_seller_account = buyer_or_seller_account_class.objects.get(**{buyer_or_seller_id_col_name: inner_model_obj_id})
            except buyer_or_seller_account_class.DoesNotExist:
                return JsonResponse({'message': f'no buyer accout with {buyer_or_seller_id_col_name}={outer_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            return JsonResponse(buyer_or_seller_account.serialize(), status=status.HTTP_200_OK, safe=False)

        def _single_user_single_buyer_or_seller_account_DELETE():
            try:
                user = User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse({'message': f'no user with user_id={outer_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            try:
                buyer_or_seller_account = buyer_or_seller_account_class.objects.get(**{buyer_or_seller_id_col_name: inner_model_obj_id})
            except buyer_or_seller_account_class.DoesNotExist:
                return JsonResponse({'message': f'no buyer accout with {buyer_or_seller_id_col_name}={outer_model_obj_id}'},
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


# GET,POST          /users/##/buyer_account
single_user_any_buyer_account = define_single_user_any_buyer_or_seller_account_closure(BuyerAccount, 'buyer_id')


# GET,DELETE        /users/##/buyer_account/##
single_user_single_buyer_account = define_single_user_single_buyer_or_seller_account_closure(BuyerAccount, 'buyer_id')


# GET,POST          /users/##/seller_account
single_user_any_seller_account = define_single_user_any_buyer_or_seller_account_closure(SellerAccount, 'seller_id')


# GET,DELETE        /users/##/seller_account/##
single_user_single_seller_account = define_single_user_single_buyer_or_seller_account_closure(SellerAccount, 'seller_id')

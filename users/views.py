#!/usr/bin/python

import bcrypt

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

from .models import User, UserPassword


def validate_user_password_input(request, user_id):
    try:
        User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'message': f'no user with user_id={user_id}'},
                            status=status.HTTP_404_NOT_FOUND)
    try:
        json_contents = json_loads(request.body)
    except JSONDecodeError:
        return JsonResponse({'message':'JSON did not parse'}, status=status.HTTP_400_BAD_REQUEST)
    keys_found = set(json_contents.keys())
    keys_found.remove('password')
    if keys_found:
        prop_expr = ', '.join(f"'{property}'" for property in keys_found)
        return JsonResponse({'message': f'unexpected propert{"ies" if len(keys_found) > 1 else "y"} '
                                        f'in input: {prop_expr}'},
                            status=status.HTTP_400_BAD_REQUEST)
    return json_contents


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
    json_contents = result
    password = json_contents['password'].encode("utf8")
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
    json_contents = result
    try:
        user_password = UserPassword.objects.get(user_id=model_obj_id)
    except UserPassword.DoesNotExist:
        return JsonResponse({'message':f'user with user_id={model_obj_id} has no password set'},
                            status=status.HTTP_404_NOT_FOUND)
    password_tocheck = json_contents['password'].encode("utf-8")
    salt = bcrypt.gensalt()
    password_onrecord_enc = bytes(user_password.encrypted_password)
    outcome = bcrypt.checkpw(password_tocheck, password_onrecord_enc)
    return JsonResponse({'authenticates':outcome}, status=status.HTTP_200_OK, safe=False)

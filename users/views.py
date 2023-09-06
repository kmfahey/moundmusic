#!/usr/bin/python3

import bcrypt
import json

from django.http.response import JsonResponse

from rest_framework.decorators import api_view
from rest_framework import status

from moundmusic.viewutils import (
    index_defclo,
    single_model_defclo,
    buyer_seller_listing_defclo,
    buyer_seller_all_defclo,
    single_buyer_seller_defclo,
    buyer_seller_acct_defclo,
)

from .models import (
    User,
    UserPassword,
    BuyerAccount,
    SellerAccount,
    ToBuyListing,
    ToSellListing,
)


# Most of the endpoint functions in this file are closures returned by
# higher-order functions defined in moundmusic.viewutils. See that file
# for the functions that are defining these endpoints.


# A utility function that represents repeated code in this file. Manages
# testing input for a endpoint that handles POSTed password input.
def validate_user_password_input(request, user_id):
    try:
        User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return JsonResponse(
            {"message": f"no user with user_id={user_id}"},
            status=status.HTTP_404_NOT_FOUND,
        )
    try:
        json_content = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"message": "JSON did not parse"}, status=status.HTTP_400_BAD_REQUEST
        )
    keys_found = set(json_content.keys())
    keys_found.remove("password")
    if keys_found:
        prop_expr = ", ".join(f"'{prop}'" for prop in keys_found)
        return JsonResponse(
            {
                "message": f'unexpected propert{"ies" if len(keys_found) > 1 else "y"} '
                f"in input: {prop_expr}"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    return json_content


# GET,POST /users
index = index_defclo(User, "user_id")


# GET,PATCH,DELETE /users/<user_id>
single_user = single_model_defclo(User, "user_id")


# POST /users/<user_id>/password
@api_view(["POST"])
def single_user_password_set_password(request, model_obj_id):
    result = validate_user_password_input(request, model_obj_id)
    if isinstance(result, JsonResponse):
        return result
    json_content = result

    # Encrypting the submitted password using the Blowfish algorithm.
    password = json_content["password"].encode("utf8")
    salt = bcrypt.gensalt()
    encrypted_password = bcrypt.hashpw(password, salt)

    # If a row exists in the user_password table then it's updated;
    # otherwise a new one is created.
    try:
        user_password = UserPassword.objects.get(user_id=model_obj_id)
    except UserPassword.DoesNotExist:
        # This handles a bug where attempting to save a new model class
        # object yields an IntegrityError that claims a pre-existing
        # primary key column value was used. This when no primary key
        # column value was set. (This bug is likely in pytest-django,
        # not psycopg2.) This workaround pre-determines the next primary
        # key column value.
        max_password_id = max(
            user_password.password_id for user_password in UserPassword.objects.filter()
        )
        user_password = UserPassword(
            password_id=max_password_id + 1,
            encrypted_password=encrypted_password,
            user_id=model_obj_id,
        )
    else:
        user_password.encrypted_password = encrypted_password

    user_password.save()
    return JsonResponse(
        user_password.serialize(), status=status.HTTP_200_OK, safe=False
    )


@api_view(["POST"])
def single_user_password_authenticate(request, model_obj_id):
    result = validate_user_password_input(request, model_obj_id)
    if isinstance(result, JsonResponse):
        return result
    json_content = result

    # If there's no password for this user stored in the database, error
    # out.
    try:
        user_password = UserPassword.objects.get(user_id=model_obj_id)
    except UserPassword.DoesNotExist:
        return JsonResponse(
            {"message": f"user with user_id={model_obj_id} has no password set"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Using bcrypt to check the plaintext password submitted against the
    # encrypted password stored.
    password_tocheck = json_content["password"].encode("utf-8")
    password_onrecord_enc = bytes(user_password.encrypted_password)
    outcome = bcrypt.checkpw(password_tocheck, password_onrecord_enc)

    return JsonResponse(
        {"authenticates": outcome}, status=status.HTTP_200_OK, safe=False
    )


# GET,POST /users/<user_id>/buyer_account
single_user_any_buyer_account = buyer_seller_acct_defclo(BuyerAccount, "buyer_id")


# GET,DELETE /users/<user_id>/buyer_account/<buyer_id>
single_user_single_buyer_account = single_buyer_seller_defclo(BuyerAccount, "buyer_id")

# GET,POST /users/<user_id>/buyer_account/<buyer_id>/listings
single_user_single_buyer_account_any_listing = buyer_seller_all_defclo(
    BuyerAccount, "buyer_id", ToBuyListing
)


# GET,DELETE /users/<user_id>/buyer_account/<ID>/listings/<listing_id>
single_user_single_buyer_account_single_listing = buyer_seller_listing_defclo(
    BuyerAccount, "buyer_id", ToBuyListing, "to_buy_listing_id"
)


# GET,POST /users/<user_id>/seller_account
single_user_any_seller_account = buyer_seller_acct_defclo(SellerAccount, "seller_id")


# GET,DELETE /users/<user_id>/seller_account/<seller_id>
single_user_single_seller_account = single_buyer_seller_defclo(
    SellerAccount, "seller_id"
)


# GET,POST /users/<user_id>/seller_account/<seller_id>/listings
single_user_single_seller_account_any_listing = buyer_seller_all_defclo(
    SellerAccount, "seller_id", ToSellListing
)


# GET,DELETE /users/<user_id>/seller_account/<seller_id>/listings/<listing_id>
single_user_single_seller_account_single_listing = buyer_seller_listing_defclo(
    SellerAccount, "seller_id", ToSellListing, "to_sell_listing_id"
)

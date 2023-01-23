#!/usr/bin/python

import pytest
import re
import random
import bcrypt
import json

from datetime import date

from django.test.client import RequestFactory
from django.http.response import JsonResponse

from .models import User, UserPassword, BuyerAccount, Album, ToBuyListing

from .views import single_user_password_set_password, single_user_password_authenticate, \
        single_user_single_buyer_account, single_user_any_buyer_account, single_user_single_buyer_account_any_listing, \
        single_user_single_buyer_account_single_listing

request_factory = RequestFactory()

matches_date_isoformat = lambda strval: bool(re.match(r"^\d{4}-\d{2}-\d{2}$", strval))

matches_2plc_decimal_format = lambda strval: bool(re.match(r"^\d+\.\d{1,2}$", strval))


@pytest.mark.django_db
def test_single_user_password_set_password_POST():
    users = User.objects.filter()
    user = random.choice(users)
    user_id = user.user_id
    password = "password123"
    request = request_factory.post(f"/users/{user_id}/password", data={"password": password},
                                   content_type="application/json")
    response = single_user_password_set_password(request, user_id)
    assert response.status_code == 200
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert "password_id" in json_content and isinstance(json_content.get("password_id"), int)
    assert "encrypted_password" in json_content and isinstance(json_content.get("encrypted_password"), str)
    assert "user_id" in json_content and isinstance(json_content.get("user_id"), int)
    password_tocheck = password.encode("utf-8")
    password_onrecord_enc = json_content["encrypted_password"].encode("utf-8")
    assert bcrypt.checkpw(password_tocheck, password_onrecord_enc)


@pytest.mark.django_db
def test_single_user_password_set_password_POST_error_nonexistent_user_id():
    users = User.objects.filter()
    user_ids = [user.user_id for user in users]
    while True:
        user_id = random.randint(1, 9999)
        if user_id not in user_ids:
            break
    password = "password123"
    request = request_factory.post(f"/users/{user_id}/password", data={"password": password},
                                   content_type="application/json")
    response = single_user_password_set_password(request, user_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] == f"no user with user_id={user_id}"


@pytest.mark.django_db
def test_single_user_password_set_password_POST_error_extra_properties():
    users = User.objects.filter()
    user = random.choice(users)
    user_id = user.user_id
    password = "password123"
    request = request_factory.post(f"/users/{user_id}/password", data={"password": password, "foo": "bar"},
                                   content_type="application/json")
    response = single_user_password_set_password(request, user_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 400
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] == "unexpected property in input: 'foo'"


@pytest.mark.django_db
def test_single_user_password_set_password_POST_conditional_user_has_no_password():
    users = User.objects.filter()
    user = random.choice(users)
    user_id = user.user_id
    user_password = UserPassword.objects.get(user_id=user_id)
    user_password.delete()
    password = "password123"
    request = request_factory.post(f"/users/{user_id}/password", data={"password": password},
                                   content_type="application/json")
    response = single_user_password_set_password(request, user_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 200
    json_content = json.loads(response.content)
    assert "password_id" in json_content and isinstance(json_content.get("password_id"), int)
    assert "encrypted_password" in json_content and isinstance(json_content.get("encrypted_password"), str)
    assert "user_id" in json_content and isinstance(json_content.get("user_id"), int)
    password_tocheck = password.encode("utf-8")
    password_onrecord_enc = json_content["encrypted_password"].encode("utf-8")
    assert bcrypt.checkpw(password_tocheck, password_onrecord_enc)


@pytest.mark.django_db
def test_single_user_password_authenticate_POST():
    users = User.objects.filter()
    user = random.choice(users)
    user_id = user.user_id
    user_password = UserPassword.objects.get(user_id=user_id)
    password = "password123"
    salt = bcrypt.gensalt()
    user_password.encrypted_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    user_password.save()
    request = request_factory.post(f"/users/{user_id}/password/authenticate", data={"password": password},
                                   content_type="application/json")
    response = single_user_password_authenticate(request, user_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 200
    json_content = json.loads(response.content)
    assert "authenticates" in json_content and json_content["authenticates"]


@pytest.mark.django_db
def test_single_user_password_authenticate_POST_error_no_password_set():
    users = User.objects.filter()
    user = random.choice(users)
    user_id = user.user_id
    user_password = UserPassword.objects.get(user_id=user_id)
    user_password.delete()
    password = "password123"
    request = request_factory.post(f"/users/{user_id}/password/authenticate", data={"password": password},
                                   content_type="application/json")
    response = single_user_password_authenticate(request, user_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] == f"user with user_id={user_id} has no password set"


# TEST single_user_any_buyer_account()
@pytest.mark.django_db
def test_single_user_any_buyer_account_GET():
    users = User.objects.filter()
    user = random.choice(users)
    while user.buyer_id is None:
        user = random.choice(users)
    user_id = user.user_id
    request = request_factory.get(f"/users/{user_id}/buyer_account")
    response = single_user_any_buyer_account(request, user_id)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert response.status_code == 200
    assert 'buyer_id' in json_content and isinstance(json_content['buyer_id'], int)
    assert 'postboard_name' in json_content and isinstance(json_content['postboard_name'], str)
    assert 'date_created' in json_content and isinstance(json_content['date_created'], str) and \
            matches_date_isoformat(json_content['date_created'])
    assert 'user_id' in json_content and isinstance(json_content['user_id'], int)


@pytest.mark.django_db
def test_single_user_any_buyer_account_GET_error_nonexistent_user_id():
    users = User.objects.filter()
    user_ids = [user.user_id for user in users]
    while True:
        user_id = random.randint(1, 9999)
        if user_id not in user_ids:
            break
    request = request_factory.get(f"/users/{user_id}/buyer_account")
    response = single_user_any_buyer_account(request, user_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] == f"no user with user_id={user_id}"


@pytest.mark.django_db
def test_single_user_any_buyer_account_GET_error_user_has_no_buyer_account():
    users = User.objects.filter(buyer_id__isnull=True)
    user = random.choice(users)
    while user.buyer_id is not None:
        user = random.choice(users)
    user_id = user.user_id
    request = request_factory.get(f"/users/{user_id}/buyer_account")
    response = single_user_any_buyer_account(request, user_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] == f"user with user_id={user_id} has no "\
                                                                     "associated buyer account"


@pytest.mark.django_db
def test_single_user_any_buyer_account_POST():
    users = User.objects.filter(buyer_id__isnull=True)
    user = random.choice(users)
    user_id = user.user_id
    new_buyer_acct_args = {"postboard_name": "A Postboard"}
    request = request_factory.post(f"/users/{user_id}/buyer_account", data=new_buyer_acct_args,
                                   content_type="application/json")
    response = single_user_any_buyer_account(request, user_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 200
    json_content = json.loads(response.content)
    assert 'buyer_id' in json_content and isinstance(json_content['buyer_id'], int)
    assert 'postboard_name' in json_content and \
            json_content['postboard_name'] == new_buyer_acct_args["postboard_name"]
    assert 'date_created' in json_content and isinstance(json_content['date_created'], str) and \
            matches_date_isoformat(json_content['date_created'])
    assert 'user_id' in json_content and isinstance(json_content['user_id'], int)


@pytest.mark.django_db
def test_single_user_any_buyer_account_POST_error_nonexistent_user_id():
    user_ids = [user.user_id for user in User.objects.filter(buyer_id__isnull=True)]
    while True:
        user_id = random.randint(1, 9999)
        if user_id not in user_ids:
            break
    new_buyer_acct_args = {"postboard_name": "A Postboard"}
    request = request_factory.post(f"/users/{user_id}/buyer_account", data=new_buyer_acct_args,
                                   content_type="application/json")
    response = single_user_any_buyer_account(request, user_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] == f"no user with user_id={user_id}"


@pytest.mark.django_db
def test_single_user_any_buyer_account_POST_error_user_already_has_a_buyer_account():
    users = User.objects.filter(buyer_id__isnull=False)
    user = random.choice(users)
    user_id, buyer_id = user.user_id, user.buyer_id
    new_buyer_acct_args = {"postboard_name": "A Postboard"}
    request = request_factory.post(f"/users/{user_id}/buyer_account", data=new_buyer_acct_args,
                                   content_type="application/json")
    response = single_user_any_buyer_account(request, user_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 409
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] == f"user with user_id={user_id} already has a "\
                                                                    f"buyer account with buyer_id={buyer_id} associated"


# TEST single_user_single_buyer_account()

@pytest.mark.django_db
def test_single_user_single_buyer_account_GET():
    users = User.objects.filter(buyer_id__isnull=False)
    user = random.choice(users)
    user_id, buyer_id = user.user_id, user.buyer_id
    request = request_factory.get(f"/users/{user_id}/buyer_account/{buyer_id}")
    response = single_user_single_buyer_account(request, user_id, buyer_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 200
    json_content = json.loads(response.content)
    assert 'buyer_id' in json_content and isinstance(json_content['buyer_id'], int)
    assert 'postboard_name' in json_content and isinstance(json_content['postboard_name'], str)
    assert 'date_created' in json_content and isinstance(json_content['date_created'], str) and \
            matches_date_isoformat(json_content['date_created'])
    assert 'user_id' in json_content and isinstance(json_content['user_id'], int)


@pytest.mark.django_db
def test_single_user_single_buyer_account_GET_error_nonexistent_user_id():
    user_ids = [user.user_id for user in User.objects.filter(buyer_id__isnull=True)]
    while True:
        user_id = random.randint(1, 9999)
        if user_id not in user_ids:
            break
    buyer_ids = [buyer_account.buyer_id for buyer_account in BuyerAccount.objects.filter()]
    buyer_id = random.choice(buyer_ids)
    request = request_factory.get(f"/users/{user_id}/buyer_account/{buyer_id}")
    response = single_user_single_buyer_account(request, user_id, buyer_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] == f"no user with user_id={user_id}"


@pytest.mark.django_db
def test_single_user_single_buyer_account_GET_error_nonexistent_buyer_id():
    user_ids = [user_account.user_id for user_account in User.objects.filter()]
    user_id = random.choice(user_ids)
    buyer_ids = [buyer_account.buyer_id for buyer_account in BuyerAccount.objects.filter()]
    while True:
        buyer_id = random.randint(1, 9999)
        if buyer_id not in buyer_ids:
            break
    request = request_factory.get(f"/users/{user_id}/buyer_account/{buyer_id}")
    response = single_user_single_buyer_account(request, user_id, buyer_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] == f"no buyer account with buyer_id={buyer_id}"


@pytest.mark.django_db
def test_single_user_single_buyer_account_DELETE():
    users = User.objects.filter(buyer_id__isnull=False)
    user = random.choice(users)
    user_id, buyer_id = user.user_id, user.buyer_id
    request = request_factory.delete(f"/users/{user_id}/buyer_account/{buyer_id}")
    response = single_user_single_buyer_account(request, user_id, buyer_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 200
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] == \
            f"buyer account with buyer_id={buyer_id} associated with user with user_id={user_id} "\
             "disassociated and deleted"


@pytest.mark.django_db
def test_single_user_single_buyer_account_DELETE_error_nonexistent_user_id():
    user_ids = [user.user_id for user in User.objects.filter(buyer_id__isnull=True)]
    while True:
        user_id = random.randint(1, 9999)
        if user_id not in user_ids:
            break
    buyer_ids = [buyer_account.buyer_id for buyer_account in BuyerAccount.objects.filter()]
    buyer_id = random.choice(buyer_ids)
    request = request_factory.delete(f"/users/{user_id}/buyer_account/{buyer_id}")
    response = single_user_single_buyer_account(request, user_id, buyer_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] == f"no user with user_id={user_id}"


@pytest.mark.django_db
def test_single_user_single_buyer_account_DELETE_error_nonexistent_buyer_id():
    user_ids = [user_account.user_id for user_account in User.objects.filter()]
    user_id = random.choice(user_ids)
    buyer_ids = [buyer_account.buyer_id for buyer_account in BuyerAccount.objects.filter()]
    while True:
        buyer_id = random.randint(1, 9999)
        if buyer_id not in buyer_ids:
            break
    request = request_factory.delete(f"/users/{user_id}/buyer_account/{buyer_id}")
    response = single_user_single_buyer_account(request, user_id, buyer_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] == f"no buyer account with buyer_id={buyer_id}"


# TEST single_user_single_buyer_account_any_listing()
@pytest.mark.django_db
def test_single_user_single_buyer_account_any_listing_GET():
    users = User.objects.filter(buyer_id__isnull=False)
    user = random.choice(users)
    user_id, buyer_id = user.user_id, user.buyer_id
    request = request_factory.get(f"/users/{user_id}/buyer_account/{buyer_id}/listings")
    response = single_user_single_buyer_account_any_listing(request, user_id, buyer_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 200
    json_content = json.loads(response.content)
    listing_dict = random.choice(json_content)
    assert "to_buy_listing_id" in listing_dict and isinstance(listing_dict["to_buy_listing_id"], int)
    assert "max_accepting_price" in listing_dict and isinstance(listing_dict["max_accepting_price"], str) and \
            matches_2plc_decimal_format(listing_dict["max_accepting_price"])
    assert "date_posted" in listing_dict and isinstance(listing_dict["date_posted"], str) and \
            matches_date_isoformat(listing_dict["date_posted"])
    assert "album_id" in listing_dict and isinstance(listing_dict["album_id"], int)
    assert "buyer_id" in listing_dict and isinstance(listing_dict["buyer_id"], int)


# TEST single_user_single_buyer_account_any_listing()
@pytest.mark.django_db
def test_single_user_single_buyer_account_any_listing_GET_error_nonexistent_user_id():
    user_ids = [user.user_id for user in User.objects.filter(buyer_id__isnull=True)]
    while True:
        user_id = random.randint(1, 9999)
        if user_id not in user_ids:
            break
    buyer_ids = [buyer_account.buyer_id for buyer_account in BuyerAccount.objects.filter()]
    buyer_id = random.choice(buyer_ids)
    request = request_factory.get(f"/users/{user_id}/buyer_account/{buyer_id}/listings")
    response = single_user_single_buyer_account_any_listing(request, user_id, buyer_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] == f"no user with user_id={user_id}"


@pytest.mark.django_db
def test_single_user_single_buyer_account_any_listing_GET_error_nonexistent_buyer_id():
    user_ids = [user_account.user_id for user_account in User.objects.filter()]
    user_id = random.choice(user_ids)
    buyer_ids = [buyer_account.buyer_id for buyer_account in BuyerAccount.objects.filter()]
    while True:
        buyer_id = random.randint(1, 9999)
        if buyer_id not in buyer_ids:
            break
    request = request_factory.get(f"/users/{user_id}/buyer_account/{buyer_id}/listings")
    response = single_user_single_buyer_account_any_listing(request, user_id, buyer_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] == f"no buyer account with buyer_id={buyer_id}"


# TEST single_user_single_buyer_account_any_listing()
@pytest.mark.django_db
def test_single_user_single_buyer_account_any_listing_POST():
    users = User.objects.filter(buyer_id__isnull=False)
    user = random.choice(users)
    user_id, buyer_id = user.user_id, user.buyer_id
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    max_accepting_price = round(1.0 + random.randint(0, 400)/100, 2)
    new_listing_args = dict(max_accepting_price=str(max_accepting_price), album_id=album_id)
    request = request_factory.post(f"/users/{user_id}/buyer_account/{buyer_id}/listings", data=new_listing_args,
                                   content_type="application/json")
    response = single_user_single_buyer_account_any_listing(request, user_id, buyer_id)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert response.status_code == 200, json_content
    assert "to_buy_listing_id" in json_content and isinstance(json_content["to_buy_listing_id"], int)
    assert "max_accepting_price" in json_content and float(json_content["max_accepting_price"]) == max_accepting_price
    assert "date_posted" in json_content and json_content["date_posted"] == date.today().isoformat()
    assert "album_id" in json_content and json_content["album_id"] == album_id
    assert "buyer_id" in json_content and json_content["buyer_id"] == buyer_id


@pytest.mark.django_db
def test_single_user_single_buyer_account_any_listing_POST_error_nonexistent_user_id():
    user_ids = [user.user_id for user in User.objects.filter(buyer_id__isnull=True)]
    while True:
        user_id = random.randint(1, 9999)
        if user_id not in user_ids:
            break
    buyer_ids = [buyer_account.buyer_id for buyer_account in BuyerAccount.objects.filter()]
    buyer_id = random.choice(buyer_ids)
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    max_accepting_price = round(1.0 + random.randint(0, 400)/100, 2)
    new_listing_args = dict(max_accepting_price=str(max_accepting_price), album_id=album_id)
    request = request_factory.post(f"/users/{user_id}/buyer_account/{buyer_id}/listings", data=new_listing_args,
                                   content_type="application/json")
    response = single_user_single_buyer_account_any_listing(request, user_id, buyer_id)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert response.status_code == 404, json_content
    assert "message" in json_content and json_content["message"] == f"no user with user_id={user_id}"


@pytest.mark.django_db
def test_single_user_single_buyer_account_any_listing_POST_error_nonexistent_buyer_id():
    user_ids = [user_account.user_id for user_account in User.objects.filter()]
    user_id = random.choice(user_ids)
    buyer_ids = [buyer_account.buyer_id for buyer_account in BuyerAccount.objects.filter()]
    while True:
        buyer_id = random.randint(1, 9999)
        if buyer_id not in buyer_ids:
            break
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    max_accepting_price = round(1.0 + random.randint(0, 400)/100, 2)
    new_listing_args = dict(max_accepting_price=str(max_accepting_price), album_id=album_id)
    request = request_factory.post(f"/users/{user_id}/buyer_account/{buyer_id}/listings", data=new_listing_args,
                                   content_type="application/json")
    response = single_user_single_buyer_account_any_listing(request, user_id, buyer_id)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert response.status_code == 404, json_content
    assert "message" in json_content and json_content["message"] == f"no buyer account with buyer_id={buyer_id}"


@pytest.mark.django_db
def test_single_user_single_buyer_account_any_listing_POST_error_missing_required_properties():
    users = User.objects.filter(buyer_id__isnull=False)
    user = random.choice(users)
    user_id, buyer_id = user.user_id, user.buyer_id
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    new_listing_args = dict(album_id=album_id)
    request = request_factory.post(f"/users/{user_id}/buyer_account/{buyer_id}/listings", data=new_listing_args,
                                   content_type="application/json")
    response = single_user_single_buyer_account_any_listing(request, user_id, buyer_id)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert response.status_code == 400, json_content
    assert "message" in json_content and json_content["message"] == "json object missing required property: 'max_accepting_price'"


@pytest.mark.django_db
def test_single_user_single_buyer_account_any_listing_POST_error_unexpected_properties():
    users = User.objects.filter(buyer_id__isnull=False)
    user = random.choice(users)
    user_id, buyer_id = user.user_id, user.buyer_id
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    max_accepting_price = round(1.0 + random.randint(0, 400)/100, 2)
    new_listing_args = dict(max_accepting_price=str(max_accepting_price), album_id=album_id, foo="bar")
    request = request_factory.post(f"/users/{user_id}/buyer_account/{buyer_id}/listings", data=new_listing_args,
                                   content_type="application/json")
    response = single_user_single_buyer_account_any_listing(request, user_id, buyer_id)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert response.status_code == 400, json_content
    assert "message" in json_content and json_content["message"] == "unexpected property in input: 'foo'"


@pytest.mark.django_db
def test_single_user_single_buyer_account_any_listing_POST_error_max_accepting_price():
    users = User.objects.filter(buyer_id__isnull=False)
    user = random.choice(users)
    user_id, buyer_id = user.user_id, user.buyer_id
    albums = Album.objects.filter()
    album = random.choice(albums)
    album_id = album.album_id
    max_accepting_price = "12.345"
    new_listing_args = dict(max_accepting_price=str(max_accepting_price), album_id=album_id)
    request = request_factory.post(f"/users/{user_id}/buyer_account/{buyer_id}/listings", data=new_listing_args,
                                   content_type="application/json")
    response = single_user_single_buyer_account_any_listing(request, user_id, buyer_id)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert response.status_code == 400, json_content
    assert "message" in json_content and json_content["message"] == "error in input, property 'max_accepting_price': "\
                                                                    "must have only two decimal places"


# TEST single_user_single_buyer_account_single_listing()
@pytest.mark.django_db
def test_single_user_single_buyer_account_single_listing_GET():
    users = User.objects.filter(buyer_id__isnull=False)
    user = random.choice(users)
    user_id, buyer_id = user.user_id, user.buyer_id
    listing_ids = [listing.to_buy_listing_id for listing in ToBuyListing.objects.filter(buyer_id=buyer_id)]
    listing_id = random.choice(listing_ids)
    request = request_factory.get(f"/users/{user_id}/buyer_account/{buyer_id}/listings/{listing_id}")
    response = single_user_single_buyer_account_single_listing(request, user_id, buyer_id, listing_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 200
    json_content = json.loads(response.content)
    assert "to_buy_listing_id" in json_content and json_content["to_buy_listing_id"] == listing_id
    assert "max_accepting_price" in json_content and isinstance(json_content["max_accepting_price"], str) and \
            matches_2plc_decimal_format(json_content["max_accepting_price"])
    assert "date_posted" in json_content and isinstance(json_content["date_posted"], str) and \
            matches_date_isoformat(json_content["date_posted"])
    assert "album_id" in json_content and isinstance(json_content["album_id"], int)
    assert "buyer_id" in json_content and json_content["buyer_id"] == buyer_id


# TEST single_user_single_buyer_account_single_listing()
@pytest.mark.django_db
def test_single_user_single_buyer_account_single_listing_GET_error_nonexistent_user_id():
    user_ids = [user.user_id for user in User.objects.filter(buyer_id__isnull=True)]
    while True:
        user_id = random.randint(1, 9999)
        if user_id not in user_ids:
            break
    buyer_ids = [buyer_account.buyer_id for buyer_account in BuyerAccount.objects.filter()]
    buyer_id = random.choice(buyer_ids)
    listing_ids = [listing.to_buy_listing_id for listing in ToBuyListing.objects.filter(buyer_id=buyer_id)]
    listing_id = random.choice(listing_ids)
    request = request_factory.get(f"/users/{user_id}/buyer_account/{buyer_id}/listings/{listing_id}")
    response = single_user_single_buyer_account_single_listing(request, user_id, buyer_id, listing_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] == f"no user with user_id={user_id}"


@pytest.mark.django_db
def test_single_user_single_buyer_account_single_listing_GET_error_nonexistent_buyer_id():
    user_ids = [user_account.user_id for user_account in User.objects.filter()]
    user_id = random.choice(user_ids)
    buyer_ids = [buyer_account.buyer_id for buyer_account in BuyerAccount.objects.filter()]
    while True:
        buyer_id = random.randint(1, 9999)
        if buyer_id not in buyer_ids:
            break
    listing_ids = [listing.to_buy_listing_id for listing in ToBuyListing.objects.filter(buyer_id=buyer_id)]
    listing_id = random.choice(listing_ids) if listing_ids else random.randint(1, 99)
    request = request_factory.get(f"/users/{user_id}/buyer_account/{buyer_id}/listings/{listing_id}")
    response = single_user_single_buyer_account_single_listing(request, user_id, buyer_id, listing_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] == f"no buyer account with buyer_id={buyer_id}"


@pytest.mark.django_db
def test_single_user_single_buyer_account_single_listing_GET_error_nonexistent_listing_id():
    users = User.objects.filter(buyer_id__isnull=False)
    user = random.choice(users)
    user_id, buyer_id = user.user_id, user.buyer_id
    listing_ids = [listing.to_buy_listing_id for listing in ToBuyListing.objects.filter(buyer_id=buyer_id)]
    while True:
        listing_id = random.randint(1, 9999)
        if listing_id not in listing_ids:
            break
    request = request_factory.get(f"/users/{user_id}/buyer_account/{buyer_id}/listings/{listing_id}")
    response = single_user_single_buyer_account_single_listing(request, user_id, buyer_id, listing_id)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert response.status_code == 404, json_content
    assert "message" in json_content and json_content["message"] == \
            f"no to-buy listing with to_buy_listing_id={listing_id}"


# TEST single_user_single_buyer_account_any_listing()
@pytest.mark.django_db
def test_single_user_single_buyer_account_single_listing_PATCH():
    users = User.objects.filter(buyer_id__isnull=False)
    user = random.choice(users)
    user_id, buyer_id = user.user_id, user.buyer_id
    listing_ids = [listing.to_buy_listing_id for listing in ToBuyListing.objects.filter(buyer_id=buyer_id)]
    listing_id = random.choice(listing_ids)
    max_accepting_price = round(1.0 + random.randint(0, 400)/100)
    patching_args = dict(max_accepting_price=str(max_accepting_price))
    request = request_factory.patch(f"/users/{user_id}/buyer_account/{buyer_id}/listings", data=patching_args,
                                    content_type="application/json")
    response = single_user_single_buyer_account_single_listing(request, user_id, buyer_id, listing_id)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert response.status_code == 200, json_content
    assert "to_buy_listing_id" in json_content and json_content["to_buy_listing_id"] == listing_id
    assert "max_accepting_price" in json_content and float(json_content["max_accepting_price"]) == max_accepting_price
    assert "date_posted" in json_content and isinstance(json_content["date_posted"], str) and \
            matches_date_isoformat(json_content["date_posted"])
    assert "album_id" in json_content and isinstance(json_content["album_id"], int)
    assert "buyer_id" in json_content and json_content["buyer_id"] == buyer_id


@pytest.mark.django_db
def test_single_user_single_buyer_account_single_listing_PATCH_error_nonexistent_user_id():
    user_ids = [user.user_id for user in User.objects.filter(buyer_id__isnull=True)]
    while True:
        user_id = random.randint(1, 9999)
        if user_id not in user_ids:
            break
    buyer_ids = [buyer_account.buyer_id for buyer_account in BuyerAccount.objects.filter()]
    buyer_id = random.choice(buyer_ids)
    listing_ids = [listing.to_buy_listing_id for listing in ToBuyListing.objects.filter(buyer_id=buyer_id)]
    listing_id = random.choice(listing_ids)
    max_accepting_price = round(1.0 + random.randint(0, 400)/100)
    patching_args = dict(max_accepting_price=str(max_accepting_price))
    request = request_factory.patch(f"/users/{user_id}/buyer_account/{buyer_id}/listings", data=patching_args,
                                    content_type="application/json")
    response = single_user_single_buyer_account_single_listing(request, user_id, buyer_id, listing_id)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert response.status_code == 404, json_content
    assert "message" in json_content and json_content["message"] == f"no user with user_id={user_id}"


@pytest.mark.django_db
def test_single_user_single_buyer_account_single_listing_PATCH_error_nonexistent_buyer_id():
    user_ids = [user_account.user_id for user_account in User.objects.filter()]
    user_id = random.choice(user_ids)
    buyer_ids = [buyer_account.buyer_id for buyer_account in BuyerAccount.objects.filter()]
    while True:
        buyer_id = random.randint(1, 9999)
        if buyer_id not in buyer_ids:
            break
    listing_ids = [listing.to_buy_listing_id for listing in ToBuyListing.objects.filter(buyer_id=buyer_id)]
    listing_id = random.choice(listing_ids) if listing_ids else random.randint(1, 99)
    max_accepting_price = round(1.0 + random.randint(0, 400)/100)
    patching_args = dict(max_accepting_price=str(max_accepting_price))
    request = request_factory.patch(f"/users/{user_id}/buyer_account/{buyer_id}/listings", data=patching_args,
                                    content_type="application/json")
    response = single_user_single_buyer_account_single_listing(request, user_id, buyer_id, listing_id)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert response.status_code == 404, json_content
    assert "message" in json_content and json_content["message"] == f"no buyer account with buyer_id={buyer_id}"


@pytest.mark.django_db
def test_single_user_single_buyer_account_single_listing_PATCH_error_nonexistent_listing_id():
    users = User.objects.filter(buyer_id__isnull=False)
    user = random.choice(users)
    user_id, buyer_id = user.user_id, user.buyer_id
    listing_ids = [listing.to_buy_listing_id for listing in ToBuyListing.objects.filter(buyer_id=buyer_id)]
    while True:
        listing_id = random.randint(1, 9999)
        if listing_id not in listing_ids:
            break
    max_accepting_price = round(1.0 + random.randint(0, 400)/100)
    patching_args = dict(max_accepting_price=str(max_accepting_price))
    request = request_factory.patch(f"/users/{user_id}/buyer_account/{buyer_id}/listings", data=patching_args,
                                    content_type="application/json")
    response = single_user_single_buyer_account_single_listing(request, user_id, buyer_id, listing_id)
    assert isinstance(response, JsonResponse)
    json_content = json.loads(response.content)
    assert response.status_code == 404, json_content
    assert "message" in json_content and json_content["message"] ==\
            f"no to-buy listing with to_buy_listing_id={listing_id}"


@pytest.mark.django_db
def test_single_user_single_buyer_account_single_listing_DELETE():
    users = User.objects.filter(buyer_id__isnull=False)
    user = random.choice(users)
    user_id, buyer_id = user.user_id, user.buyer_id
    listing_ids = [listing.to_buy_listing_id for listing in ToBuyListing.objects.filter(buyer_id=buyer_id)]
    listing_id = random.choice(listing_ids)
    request = request_factory.delete(f"/users/{user_id}/buyer_account/{buyer_id}/listings/{listing_id}")
    response = single_user_single_buyer_account_single_listing(request, user_id, buyer_id, listing_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 200
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] ==\
            f"to-buy listing with to_buy_listing_id={listing_id} deleted"


# TEST single_user_single_buyer_account_single_listing()
@pytest.mark.django_db
def test_single_user_single_buyer_account_single_listing_DELETE_error_nonexistent_user_id():
    user_ids = [user.user_id for user in User.objects.filter(buyer_id__isnull=True)]
    while True:
        user_id = random.randint(1, 9999)
        if user_id not in user_ids:
            break
    buyer_ids = [buyer_account.buyer_id for buyer_account in BuyerAccount.objects.filter()]
    buyer_id = random.choice(buyer_ids)
    listing_ids = [listing.to_buy_listing_id for listing in ToBuyListing.objects.filter(buyer_id=buyer_id)]
    listing_id = random.choice(listing_ids)
    request = request_factory.delete(f"/users/{user_id}/buyer_account/{buyer_id}/listings/{listing_id}")
    response = single_user_single_buyer_account_single_listing(request, user_id, buyer_id, listing_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] == f"no user with user_id={user_id}"


@pytest.mark.django_db
def test_single_user_single_buyer_account_single_listing_DELETE_error_nonexistent_buyer_id():
    user_ids = [user_account.user_id for user_account in User.objects.filter()]
    user_id = random.choice(user_ids)
    buyer_ids = [buyer_account.buyer_id for buyer_account in BuyerAccount.objects.filter()]
    while True:
        buyer_id = random.randint(1, 9999)
        if buyer_id not in buyer_ids:
            break
    listing_ids = [listing.to_buy_listing_id for listing in ToBuyListing.objects.filter(buyer_id=buyer_id)]
    listing_id = random.choice(listing_ids) if listing_ids else random.randint(1, 99)
    request = request_factory.delete(f"/users/{user_id}/buyer_account/{buyer_id}/listings/{listing_id}")
    response = single_user_single_buyer_account_single_listing(request, user_id, buyer_id, listing_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] == f"no buyer account with buyer_id={buyer_id}"


@pytest.mark.django_db
def test_single_user_single_buyer_account_single_listing_DELETE_error_nonexistent_listing_id():
    users = User.objects.filter(buyer_id__isnull=False)
    user = random.choice(users)
    user_id, buyer_id = user.user_id, user.buyer_id
    listing_ids = [listing.to_buy_listing_id for listing in ToBuyListing.objects.filter(buyer_id=buyer_id)]
    while True:
        listing_id = random.randint(1, 9999)
        if listing_id not in listing_ids:
            break
    request = request_factory.delete(f"/users/{user_id}/buyer_account/{buyer_id}/listings/{listing_id}")
    response = single_user_single_buyer_account_single_listing(request, user_id, buyer_id, listing_id)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 404
    json_content = json.loads(response.content)
    assert "message" in json_content and json_content["message"] ==\
            f"no to-buy listing with to_buy_listing_id={listing_id}"

# NOTE
#
# The corresponding endpoint functions for the *seller* subordinate endpoint
# suite are not tested.
#
# This is because the endpoint functions that *were* just tested,
# single_user_single_buyer_account(), single_user_any_buyer_account(),
# single_user_single_buyer_account_any_listing(), and
# single_user_single_buyer_account_single_listing(), are implemented
# using closures returned by higher-order functions (implemented in
# moundmusic.viewutils, q.v.) that are also called to return the corresponding
# seller-side endpoint functions.
#
# Testing the aforementioned closures implicitly tests the higher-order
# functions that returned them; that ensures the seller-side functions are
# correct, since it's the same code either way. Testing the seller-side
# endpoint functions would be duplicative.

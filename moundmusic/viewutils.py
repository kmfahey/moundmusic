#!/usr/bin/python3

import json

from datetime import date

from django.http import HttpResponse
from django.http.response import JsonResponse

from rest_framework import status
from rest_framework.decorators import api_view

from users.models import User, BuyerAccount, ToBuyListing


# A word on the endpoint function structure used in most of the endpoint
# functions returned by these higher-order functions:
#
# With django's rest framework, an endpoint function has to handle
# all the methods that endpoint accepts. Where that's more than one
# method, this pattern is used: an inline function is written for
# each method, and the body of the function consists of a tail-call
# to moundmusic.viewutils.func_dispatch(), which itself
# tail-calls the inline function that matches the method that's being
# handled.


# This function validates input from a POST or PATCH submission of
# an object intended to create a new row or modify an existing one.
# It relies on the model class's __columns__ value, which is a dict
# associating whose keys are all the columns in the table, and whose
# values are python types to conform the data to. It also uses the model
# class's __nullable__ value, which is a tuple listing keys whose values
# may be None.
def validate_input(model_class, input_argd, all_nullable=False):
    validated_dict = dict()
    # Checking for property names not germane to this table.
    diff = set(input_argd.keys()) - set(model_class.__columns__)
    if diff:
        diff_expr = ", ".join(f"'{key}'" for key in diff)
        raise ValueError(
            f"unexpected propert"
            + ("ies" if len(diff) > 1 else "y")
            + f" in input: {diff_expr}"
        )

    # Iterating across __columns__, testing each value in input_argd
    # according to the python type.
    for column, value in input_argd.items():
        column_type = model_class.__columns__[column]
        if value is None:
            # If all_nullable=True or the model class accepts None for
            # that value, error out.
            if not all_nullable and column not in model_class.__nullable_cols__:
                raise ValueError(
                    f"value for '{column}' is null and column not nullable"
                )
        elif column_type is int:
            # Testing whether the value casts to int.
            try:
                value = int(value)
            except ValueError:
                raise ValueError(
                    f"value for '{column}' isn't an integer: " + str(value)
                )
            # Testing whether the value is nonnegative. There's no use
            # of integers in this package that doesn't require them to
            # be nonnegative.
            if value <= 0:
                raise ValueError(
                    f"value for '{column}' isn't greater than 0: " + str(value)
                )
        elif column_type is str and not len(value):
            # If the value is a zero-length string, error out.
            raise ValueError(f"value for '{column}' is a string of zero length")
        elif column_type is date:
            # Testing whether the value conforms to the iso 8601 format
            # (YYYY-MM-DD) that datetime.date can instance a date from.
            try:
                value = date.fromisoformat(value)
            except ValueError:
                raise ValueError(
                    f"value for '{column}' isn't in format YYYY-MM-DD and "
                    + "column is a DATE"
                )
        elif isinstance(column_type, tuple):
            # If the __columns__ value is a tuple, then this is a
            # postgres enumerated type and the input value must appear
            # in that tuple.
            if value not in column_type:
                enum_expr = (
                    ", ".join(f"'{option}'" for option in column_type[:-1])
                    + f" or '{column_type[-1]}'"
                )
                raise ValueError(
                    f"value for '{column}' not one of {enum_expr} and column "
                    + "is an ENUM type"
                )
        validated_dict[column] = value
    return validated_dict


# This utility function is used by every endpoint function that manages
# more than one http method. They're written with inline functions for
# each http method, and then this function is tail-called to dispatch
# the correct one.
def func_dispatch(functions, request):
    # Building a dispatch table.
    dispatch_table = dict()
    for function in functions:
        # Each inline function embeds the http method it handles as the
        # last word in their name.
        func_name = function.__name__
        _, method = func_name.rsplit("_", 1)
        dispatch_table[method] = function
    method = request.method.lower()
    # Tail calling the inline function for this http method, or erroring
    # out if it's not defined (ie. this endpoint was accessed using an
    # unsupported http method).
    if method in dispatch_table:
        return dispatch_table[method]()
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


# Refactored out some repeated code validating POST requests.
def validate_post_request(request, model_class, all_nullable=False):
    # Testing for valid JSON or erroring out.
    try:
        posted_json = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"message": "JSON did not parse"}, status=status.HTTP_400_BAD_REQUEST
        )
    # Testing for valid arguments (in the JSON object) or erroring out.
    try:
        validated_args = validate_input(
            model_class, posted_json, all_nullable=all_nullable
        )
    except ValueError as exception:
        return JsonResponse(
            {"message": exception.args[0]}, status=status.HTTP_400_BAD_REQUEST
        )
    # Input is valid, returning.
    return validated_args


# Refactored out some repeated code validating PATCH requests.
def validate_patch_request(request, model_class, model_id_attr_name, model_id_attr_val):
    # Trying to find a row in the `model_class._meta.db_table`
    # table where the `model_id_attr_name` column has the value
    # `model_id_attr_val`, or erroring out.
    try:
        model_instance = model_class.objects.get(
            **{model_id_attr_name: model_id_attr_val}
        )
    except model_class.DoesNotExist:
        return JsonResponse(
            {
                "message": f"no {model_class.__name__.lower()} with "
                f"{model_id_attr_name}={model_id_attr_val}"
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    # Testing for valid JSON or erroring out.
    try:
        posted_json = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"message": "JSON did not parse"}, status=status.HTTP_400_BAD_REQUEST
        )
    # Testing for non-empty JSON or erroring out.
    if not len(posted_json):
        return JsonResponse(
            {"message": "empty JSON object"}, status=status.HTTP_400_BAD_REQUEST
        )
    # Testing for valid arguments (in the JSON object) or erroring out.
    try:
        validated_input = validate_input(model_class, posted_json, all_nullable=True)
    except ValueError as exception:
        return JsonResponse(
            {"message": exception.args[0]}, status=status.HTTP_400_BAD_REQUEST
        )
    # Input is valid, returning.
    return model_instance, validated_input


# A utility function used to validate two model classes with id values
# and the model class for the bridge table that connects them.
def validate_bridgetab_models(
    left_model_class,
    left_model_attr_name,
    left_model_attr_value,
    right_model_class,
    right_model_attr_name,
    right_model_attr_value,
    bridge_model_class,
):
    # Trying to find a row in the `left_model_class._meta.db_table`
    # table where the `left_model_attr_name` column has the value
    # `left_model_attr_value`, or erroring out.
    try:
        left_model_obj = left_model_class.objects.get(
            **{left_model_attr_name: left_model_attr_value}
        )
    except left_model_class.DoesNotExist:
        return JsonResponse(
            {
                "message": f"no {left_model_class.__name__.lower()} with "
                + f"{left_model_attr_name}={left_model_attr_value}"
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    # Trying to find a row in the `right_model_class._meta.db_table`
    # table where the `right_model_attr_name` column has the value
    # `right_model_attr_value`, or erroring out.
    try:
        right_model_obj = right_model_class.objects.get(
            **{right_model_attr_name: right_model_attr_value}
        )
    except right_model_class.DoesNotExist:
        return JsonResponse(
            {
                "message": f"no {right_model_class.__name__.lower()} with "
                + f"{right_model_attr_name}={right_model_attr_value}"
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    # Trying to find a row in the `bridge_model_class._meta.db_table`
    # table where the `left_model_attr_name` column value is
    # `left_model_attr_value` and the `right_model_attr_name` column
    # value is `right_model_attr_value`, or erroring out.
    try:
        bridge_row = bridge_model_class.objects.get(
            **{
                left_model_attr_name: left_model_attr_value,
                right_model_attr_name: right_model_attr_value,
            }
        )
    except bridge_model_class.DoesNotExist:
        return JsonResponse(
            {
                "message": f"{left_model_class.__name__.lower()} with "
                + f"{left_model_attr_name}={left_model_attr_value} not "
                + f"associated with {right_model_class.__name__.lower()} with "
                + f"{right_model_attr_name}={right_model_attr_value}"
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    # Input is valid, returning.
    return left_model_obj, right_model_obj, bridge_row


# BEGIN higher-order functions
#
# Each function from this point forward defines and returns a closure
# that can handle an endpoint.


# Handles index endpoints.
def index_defclo(model_class, model_id_attr_name):

    # BEGIN closure
    @api_view(["GET", "POST"])
    def index_closure(request):
        def _index_get():
            return JsonResponse(
                [model_obj.serialize() for model_obj in model_class.objects.all()],
                status=status.HTTP_200_OK,
                safe=False,
            )

        def _index_post():
            result = validate_post_request(request, model_class)
            if isinstance(result, JsonResponse):
                return result
            else:
                validated_args = result
            # If the input attempts to set the primary key column of the
            # `model_class._meta.db_table` table, error out.
            if model_id_attr_name in validated_args:
                return JsonResponse(
                    {
                        "message": f"a new {model_class.__name__.lower()} "
                        + f"object must not have a {model_id_attr_name} value"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # This handles a bug where attempting to save a new model
            # class object yields an IntegrityError that claims a
            # pre-existing primary key column value was used. This
            # when no primary key column value was set. (This bug is
            # likely in pytest-django, not psycopg2.) This workaround
            # pre-determines the next primary key column value.
            max_id_attr_value = max(
                getattr(row_obj, model_id_attr_name)
                for row_obj in model_class.objects.filter()
            )
            new_args = validated_args.copy()
            new_args[model_id_attr_name] = max_id_attr_value + 1
            new_model_obj = model_class(**new_args)
            new_model_obj.save()
            return JsonResponse(
                new_model_obj.serialize(), status=status.HTTP_201_CREATED
            )

        return func_dispatch((_index_get, _index_post), request)

    # END closure

    return index_closure


# Handles endpoints of the form "GET,PATCH,DELETE /<model_class>"
def single_model_defclo(model_class, model_id_attr_name):
    # BEGIN closure
    @api_view(["GET", "PATCH", "DELETE"])
    def single_model_closure(request, model_obj_id):
        def _single_model_get():
            # If the `model_class._meta.db_table` table doesn't have a
            # row where the `model_id_attr_name` column (ie. the primary
            # key) has the value `model_obj_id`, error out.
            try:
                model_obj = model_class.objects.get(
                    **{model_id_attr_name: model_obj_id}
                )
            except model_class.DoesNotExist:
                return JsonResponse(
                    {
                        "message": f"no {model_class.__name__.lower()} with "
                        + f"{model_id_attr_name}={model_obj_id}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            return JsonResponse(model_obj.serialize(), status=status.HTTP_200_OK)

        def _single_model_patch():

            # Validating input using a shorthand function.
            retval = validate_patch_request(
                request, model_class, model_id_attr_name, model_obj_id
            )
            if isinstance(retval, JsonResponse):
                return retval
            else:
                model_obj, validated_input = retval

            # If the input attempts to set the primary key column of the
            # `model_class._meta.db_table` table, error out.
            if model_id_attr_name in validated_input:
                return JsonResponse(
                    {
                        "message": f"an updated "
                        + f"{model_class.__name__.lower()} object must not "
                        + f"have a {model_id_attr_name} value"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Set attributes on the model class object from the input,
            # then save the object to storage.
            for column, column_value in validated_input.items():
                setattr(model_obj, column, column_value)
            model_obj.save()
            return JsonResponse(model_obj.serialize(), status=status.HTTP_200_OK)

        def _single_model_delete():
            # If the `model_class._meta.db_table` table doesn't have a
            # row where the `model_id_attr_name` column (ie. the primary
            # key) has the value `model_obj_id`, error out.
            try:
                model_obj = model_class.objects.get(
                    **{model_id_attr_name: model_obj_id}
                )
            except model_class.DoesNotExist:
                return JsonResponse(
                    {
                        "message": f"no {model_class.__name__.lower()} with "
                        + f"{model_id_attr_name}={model_obj_id}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Delete the object from storage.
            model_obj.delete()
            return JsonResponse(
                {
                    "message": f"{model_class.__name__.lower()} with "
                    + f"{model_id_attr_name}={model_obj_id} deleted"
                },
                status=status.HTTP_200_OK,
            )

        return func_dispatch(
            (_single_model_get, _single_model_patch, _single_model_delete), request
        )

    # END closure

    return single_model_closure


# Handle endpoints of the form
# "GET,POST /<outer_model>/<outer_id>/<inner_model>"
def outer_id_inner_list_defclo(
    outer_model_class,
    outer_model_id_attr_name,
    inner_model_class,
    inner_model_id_attr_name,
    bridge_class,
):
    # BEGIN closure
    @api_view(["GET", "POST"])
    def outer_id_inner_list_closure(request, outer_model_obj_id):

        # This method fetches all members of the inner class associated
        # with the member of the outer class mentioned. For example,
        # GET /albums/<albumId>/songs would return all songs with rows
        # in the albums_songs_bridge table associating them with that
        # albumId.
        def _outer_id_inner_list_get():
            # If the `outer_model_class._meta.db_table` table doesn't
            # have a row where the `outer_model_id_attr_name` column
            # (ie. the primary key) has the value `outer_model_obj_id`,
            # error out.
            try:
                outer_model_class.objects.get(
                    **{outer_model_id_attr_name: outer_model_obj_id}
                )
            except outer_model_class.DoesNotExist:
                return JsonResponse(
                    {
                        "message": f"no {outer_model_class.__name__.lower()} "
                        + f"with {outer_model_id_attr_name}="
                        + str(outer_model_obj_id)
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            # Uses the bridge table to fetch primary key values for the
            # `inner_model_id_attr_name._meta.db_table`, then fetches
            # the object with that id from that model class, for each
            # id, and serializes the object so it can be jsonified.
            bridge_rows = bridge_class.objects.filter(
                **{outer_model_id_attr_name: outer_model_obj_id}
            )
            return_list = [
                inner_model_class.objects.get(
                    **{
                        inner_model_id_attr_name: getattr(
                            bridge_row, inner_model_id_attr_name
                        )
                    }
                ).serialize()
                for bridge_row in bridge_rows
            ]
            return JsonResponse(return_list, status=status.HTTP_200_OK, safe=False)

        # This method attempts to associate the member of the 2nd
        # class with the member of the 1st class. For example, POST
        # {song_id:<songId>} to /albums/<albumId>/songs would attempt
        # to add a row in the albums_songs_bridge table associating
        # <songId> with <albumId>.
        def _outer_id_inner_list_post():
            # If the `outer_model_class._meta.db_table` table doesn't
            # have a row where the `outer_model_id_attr_name` column
            # (ie. the primary key) has the value `outer_model_obj_id`,
            # error out.
            try:
                outer_model_class.objects.get(
                    **{outer_model_id_attr_name: outer_model_obj_id}
                )
            except outer_model_class.DoesNotExist:
                return JsonResponse(
                    {
                        "message": f"no {outer_model_class.__name__.lower()} "
                        + f"with {outer_model_id_attr_name}="
                        + str(outer_model_obj_id)
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Testing for valid JSON or erroring out.
            try:
                posted_json = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse(
                    {"message": "JSON did not parse"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # The only valid property for this request is the primary
            # key column. If any others are found, error out.
            diff = set(posted_json.keys()) - {inner_model_id_attr_name}
            if diff:
                prop_expr = ", ".join(f"'{prop}'" for prop in diff)
                return JsonResponse(
                    {
                        "message": f"unexpected propert"
                        + ("ies" if len(diff) > 1 else "y")
                        + f" in input: {prop_expr}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            inner_model_obj_id = posted_json[inner_model_id_attr_name]

            # Testing whether a row in the
            # `inner_model_class._meta.db_table` table with the column
            # `inner_model_id_attr_name` (ie. the primary key) having
            # the value `inner_model_obj_id` exists, or erroring out.
            try:
                inner_model_obj = inner_model_class.objects.get(
                    **{inner_model_id_attr_name: inner_model_obj_id}
                )
            except inner_model_class.DoesNotExist:
                return JsonResponse(
                    {
                        "message": f"no {inner_model_class.__name__.lower()} "
                        + f"with {inner_model_id_attr_name}="
                        + str(inner_model_obj_id)
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            # Testing whether a row exists in the
            # `bridge_class._meta.db_table` bridge table where
            # the value of the `outer_model_id_attr_name` column
            # is `outer_model_obj_id` and the value of the
            # `inner_model_id_attr_name` column is `inner_model_obj_id`.
            # If so, error out, because the association this request is
            # trying to make already exists.
            try:
                bridge_class.objects.get(
                    **{
                        outer_model_id_attr_name: outer_model_obj_id,
                        inner_model_id_attr_name: inner_model_obj_id,
                    }
                )
            except bridge_class.DoesNotExist:
                pass
            else:
                return JsonResponse(
                    {
                        "message": f"association between "
                        + outer_model_class.__name__.lower()
                        + " with "
                        + f"{outer_model_id_attr_name}={outer_model_obj_id} "
                        + f"and {inner_model_class.__name__.lower()} with "
                        + f"{inner_model_id_attr_name}={inner_model_obj_id} "
                        + "already exists"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Creating the association in the bridge table and saving
            # it.
            bridge_table_name = bridge_class._meta.db_table
            bridge_table_id_col = f"{bridge_table_name}_id"

            # This handles a bug where attempting to save a new model
            # class object yields an IntegrityError that claims a
            # pre-existing primary key column value was used. This
            # when no primary key column value was set. (This bug is
            # likely in pytest-django, not psycopg2.) This workaround
            # pre-determines the next primary key column value.
            max_bridge_row_id = max(
                getattr(bridge_row, bridge_table_id_col)
                for bridge_row in bridge_class.objects.filter()
            )
            bridge_row = bridge_class(
                **{
                    bridge_table_id_col: max_bridge_row_id + 1,
                    outer_model_id_attr_name: outer_model_obj_id,
                    inner_model_id_attr_name: inner_model_obj_id,
                }
            )
            bridge_row.save()
            return JsonResponse(inner_model_obj.serialize(), status=status.HTTP_200_OK)

        return func_dispatch(
            (
                _outer_id_inner_list_get,
                _outer_id_inner_list_post,
            ),
            request,
        )
        # END closure

    return outer_id_inner_list_closure


# Handles requests of the form
# "GET,DELETE /<outer_model>/<outer_id>/<inner_model>/<inner_id>"
def outer_id_inner_id_defclo(
    outer_model_class,
    outer_model_id_attr_name,
    inner_model_class,
    inner_model_id_attr_name,
    bridge_class,
):
    # BEGIN closure
    @api_view(["GET", "DELETE"])
    def outer_id_inner_id_closure(request, outer_model_obj_id, inner_model_obj_id):

        # Handles a GET request for a single member of the outer
        # class by ID, and a single member of the inner class by
        # ID, where the 2nd member is returned. For example, a GET
        # /albums/<albumId>/songs/<songId> would return a JSON object of
        # the song with that songId.
        def _outer_id_inner_id_get():
            result = validate_bridgetab_models(
                outer_model_class,
                outer_model_id_attr_name,
                outer_model_obj_id,
                inner_model_class,
                inner_model_id_attr_name,
                inner_model_obj_id,
                bridge_class,
            )
            if isinstance(result, JsonResponse):
                return result
            else:
                _, inner_model, _ = result
            return JsonResponse(inner_model.serialize(), status=status.HTTP_200_OK)

        # Handles a DELETE request for a single member of the outer
        # class by ID, and a single member of the inner class by ID,
        # where the two are disassociated in the relevant bridge table.
        # For example, a DELETE /genres/<genreId>/songs/<songId> would
        # remove the bridge table row that linked <genreId> to <songId>.
        def _outer_id_inner_id_delete():
            # Validating input for bridge-table-specific operations like
            # this one.
            result = validate_bridgetab_models(
                outer_model_class,
                outer_model_id_attr_name,
                outer_model_obj_id,
                inner_model_class,
                inner_model_id_attr_name,
                inner_model_obj_id,
                bridge_class,
            )
            if isinstance(result, JsonResponse):
                return result
            else:
                _, _, bridge_row = result
            bridge_row.delete()
            return JsonResponse(
                {
                    "message": f"association between "
                    + outer_model_class.__name__.lower()
                    + f" with {outer_model_id_attr_name}={outer_model_obj_id} "
                    + "and "
                    + inner_model_class.__name__.lower()
                    + f" with {inner_model_id_attr_name}={inner_model_obj_id} "
                    + "deleted"
                },
                status=status.HTTP_200_OK,
            )

        return func_dispatch(
            (
                _outer_id_inner_id_get,
                _outer_id_inner_id_delete,
            ),
            request,
        )

    # END closure

    return outer_id_inner_id_closure


# BUYER/SELLER
#
# From this point forward, all remaining higher-order functions are
# specific to users.views; moved here for clarity. These handle the
# mirror symmetry between the buyer_account table and seller_account
# table cases.

# Handles requests of the form
# "GET,POST /users/<user_id>/(buyer|seller)_account"
def buyer_seller_acct_defclo(
    buyer_or_seller_account_class, buyer_or_seller_id_col_name
):
    # BEGIN closure
    @api_view(["GET", "POST"])
    def buyer_seller_acct_closure(request, outer_model_obj_id):

        # Handles a GET request where a single user is specified,
        # and the associated buyer/seller account is expected. For
        # example, a GET /users/<user_id>/buyer_account would return the
        # associated buyer account.
        def _buyer_seller_acct_get():
            # Tests whether a User with user_id=<outer_model_obj_id>
            # exists, or errors out.
            try:
                user = User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse(
                    {"message": f"no user with user_id={outer_model_obj_id}"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            # Tests whether that user has a buyer/seller id value set,
            # or errors out.
            if getattr(user, buyer_or_seller_id_col_name) is None:
                return JsonResponse(
                    {
                        "message": f"user with user_id={outer_model_obj_id} "
                        + "has no associated buyer account"
                    },
                    content_type="application/json",
                    status=status.HTTP_404_NOT_FOUND,
                )
            # Tests whether a buyer/seller account exists with that id,
            # or erros out.
            try:
                buyer_account = buyer_or_seller_account_class.objects.get(
                    user_id=outer_model_obj_id
                )
            except buyer_or_seller_account_class.DoesNotExist:
                return JsonResponse(
                    {
                        "message": f"user with user_id={outer_model_obj_id} "
                        + "has no associated buyer account"
                    },
                    content_type="application/json",
                    status=status.HTTP_404_NOT_FOUND,
                )
            return JsonResponse(
                buyer_account.serialize(), status=status.HTTP_200_OK, safe=False
            )

        # Handles a POST request where a single user is specified, and
        # the request is attempting to create a buyer/seller account
        # for it. For example, a POST to /users/<user_id>/buyer_account
        # would create a new buyer_account and associate it with the
        # user with user_id=<user_id>.
        def _buyer_seller_acct_post():

            # Tests whether a user with that id exists, or errors out.
            try:
                user = User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse(
                    {"message": f"no user with user_id={outer_model_obj_id}"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            buyer_or_seller_id = getattr(user, buyer_or_seller_id_col_name)
            kind_of_account = buyer_or_seller_id_col_name.split("_")[0]

            # Tests whether there's already a buyer/seller id set on the
            # user object, and if so errors out.
            if buyer_or_seller_id is not None:
                return JsonResponse(
                    {
                        "message": f"user with user_id={outer_model_obj_id} "
                        + f"already has a {kind_of_account} account with "
                        + f"{buyer_or_seller_id_col_name}={buyer_or_seller_id} "
                        + "associated"
                    },
                    content_type="application/json",
                    status=status.HTTP_409_CONFLICT,
                )

            # Validating input.
            result = validate_post_request(request, buyer_or_seller_account_class)
            if isinstance(result, JsonResponse):
                return result
            json_content = result

            # The only valid input property is the name associated
            # with the account. Tests whether any other properties are
            # present, if so errors out.
            keys_found = set(json_content.keys())
            if buyer_or_seller_account_class is BuyerAccount:
                keys_found.remove("postboard_name")
            else:
                keys_found.remove("storefront_name")
            if keys_found:
                prop_expr = ", ".join(f"'{prop}'" for prop in keys_found)
                return JsonResponse(
                    {
                        "message": f"unexpected propert"
                        + ("ies" if len(keys_found) > 1 else "y")
                        + f" in input: {prop_expr}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Creates the object,
            json_content["date_created"] = date.today()
            json_content["user_id"] = user.user_id

            # This handles a bug where attempting to save a new model
            # class object yields an IntegrityError that claims a
            # pre-existing primary key column value was used. This
            # when no primary key column value was set. (This bug is
            # likely in pytest-django, not psycopg2.) This workaround
            # pre-determines the next primary key column value.
            max_buyer_or_seller_account_id = max(
                getattr(buyer_or_seller_account, buyer_or_seller_id_col_name)
                for buyer_or_seller_account in buyer_or_seller_account_class.objects.filter()
            )
            new_args = json_content.copy()
            new_args[buyer_or_seller_id_col_name] = max_buyer_or_seller_account_id + 1
            buyer_or_seller_account = buyer_or_seller_account_class(**new_args)
            buyer_or_seller_account.user_id = user.user_id
            buyer_or_seller_account.save()
            setattr(
                user,
                buyer_or_seller_id_col_name,
                getattr(buyer_or_seller_account, buyer_or_seller_id_col_name),
            )
            user.save()
            return JsonResponse(
                buyer_or_seller_account.serialize(), status=status.HTTP_200_OK
            )

        return func_dispatch(
            (
                _buyer_seller_acct_get,
                _buyer_seller_acct_post,
            ),
            request,
        )

    # END closure

    return buyer_seller_acct_closure


# Handles requests of the form "GET,DELETE
# /users/<user_id>/(buyer|seller)_account/<(buyer|seller)_id>"
def single_buyer_seller_defclo(
    buyer_or_seller_account_class, buyer_or_seller_id_col_name
):

    # BEGIN closure
    @api_view(["GET", "DELETE"])
    def single_buyer_seller_closure(request, outer_model_obj_id, inner_model_obj_id):

        # Handles requests of the form GET
        # /users/<user_id>/(buyer|seller)_account/<(buyer|seller)_id>.
        # For example, GET /users/<user_id>/buyer_account/<buyer_id>
        # would return a serialization of the buyer_account table row
        # with a buyer_id value equal to the buyer_id value set on that
        # user object.
        def _single_buyer_seller_get():
            # Tests whether a matching user with
            # user_id=`outer_model_obj_id` exists, or errors out.
            try:
                User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse(
                    {"message": f"no user with user_id={outer_model_obj_id}"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            # Tests whether a
            # `buyer_or_seller_account_class._meta.db_table` row with
            # the column `buyer_or_seller_id_col_name` value (ie. the
            # primary key) equal to `inner_model_obj_id`, or errors out.
            try:
                buyer_or_seller_account = buyer_or_seller_account_class.objects.get(
                    **{buyer_or_seller_id_col_name: inner_model_obj_id}
                )
            except buyer_or_seller_account_class.DoesNotExist:
                return JsonResponse(
                    {
                        "message": f"no buyer account with "
                        + f"{buyer_or_seller_id_col_name}={inner_model_obj_id}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            return JsonResponse(
                buyer_or_seller_account.serialize(),
                status=status.HTTP_200_OK,
                safe=False,
            )

        # Handles requests of the form DELETE
        # /users/<user_id>/(buyer|seller)_account/<(buyer|seller)_id>.
        # For example, DELETE /users/<user_id>/buyer_account/<buyer_id>
        # would disassociate the buyer account with id <buyer_id>
        # from the user with user_id <user_id>, and delete that buyer
        # account.
        def _single_buyer_seller_delete():
            # Tests whether a matching user with
            # user_id=`outer_model_obj_id` exists, or errors out.
            try:
                user = User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse(
                    {"message": f"no user with user_id={outer_model_obj_id}"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            # Tests whether a
            # `buyer_or_seller_account_class._meta.db_table` row with
            # the column `buyer_or_seller_id_col_name` value (ie. the
            # primary key) equal to `inner_model_obj_id`, or errors out.
            try:
                buyer_or_seller_account = buyer_or_seller_account_class.objects.get(
                    **{buyer_or_seller_id_col_name: inner_model_obj_id}
                )
            except buyer_or_seller_account_class.DoesNotExist:
                return JsonResponse(
                    {
                        "message": f"no buyer account with "
                        + f"{buyer_or_seller_id_col_name}={inner_model_obj_id}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            # Removes that buyer_id value from the user and saves, then
            # deletes the account.
            setattr(user, buyer_or_seller_id_col_name, None)
            user.save()
            kind_of_account = buyer_or_seller_id_col_name.split("_")[0]
            buyer_or_seller_account.delete()
            return JsonResponse(
                {
                    "message": f"{kind_of_account} account with "
                    + f"{buyer_or_seller_id_col_name}={inner_model_obj_id} "
                    + f"associated with user with "
                    + f"user_id={outer_model_obj_id} disassociated and deleted"
                },
                status=status.HTTP_200_OK,
            )

        return func_dispatch(
            (
                _single_buyer_seller_get,
                _single_buyer_seller_delete,
            ),
            request,
        )

    # END closure

    return single_buyer_seller_closure


# Handles requests of the form "GET,POST
# /users/<user_id>/(buyer|seller)_account/<(buyer|seller)_id>/listings"
def buyer_seller_all_defclo(
    buyer_or_seller_class, buyer_or_seller_id_col_name, to_buy_or_to_sell_listing_class
):

    # BEGIN closure
    @api_view(["GET", "POST"])
    def buyer_seller_all_closure(request, outer_model_obj_id, inner_model_obj_id):
        # Handles GET requests, given a member of the outer
        # class and a member of the inner class, for all
        # members of the third class. For example, GET
        # /users/<user_id>/buyer_account/<buyer_id>/listings would
        # return all to-buy listings associated with that buyer_id.
        def _buyer_seller_all_get():
            # Tests whether a matching user with
            # user_id=`outer_model_obj_id` exists, or errors out.
            try:
                User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse(
                    {"message": f"no user with user_id={outer_model_obj_id}"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            # Tests whether a
            # `buyer_or_seller_account_class._meta.db_table` row with
            # the column `buyer_or_seller_id_col_name` value (ie. the
            # primary key) equal to `inner_model_obj_id`, or errors out.
            kind_of_account = buyer_or_seller_id_col_name.split("_")[0]
            try:
                buyer_or_seller_class.objects.get(
                    **{buyer_or_seller_id_col_name: inner_model_obj_id}
                )
            except buyer_or_seller_class.DoesNotExist:
                return JsonResponse(
                    {
                        "message": f"no {kind_of_account} account with "
                        + f"{buyer_or_seller_id_col_name}={inner_model_obj_id}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            # Fetches all rows in
            # `to_buy_or_to_sell_listing_class._meta.db_table` with the
            # column `buyer_or_seller_id_col_name` having the value
            # `inner_model_obj_id`, serializes them and returns the
            # list.
            listings = to_buy_or_to_sell_listing_class.objects.filter(
                **{buyer_or_seller_id_col_name: inner_model_obj_id}
            )
            listings_serialized = [listing.serialize() for listing in listings]
            return JsonResponse(
                listings_serialized, status=status.HTTP_200_OK, safe=False
            )

        # Handles GET requests, given a member of the outer
        # class and a member of the inner class, for all
        # members of the third class. For example, POST
        # /users/<user_id>/buyer_account/<buyer_id>/listings would
        # create a new listing and associate it with that buyer_id.
        def _buyer_seller_all_post():

            # Tests whether a matching user with
            # user_id=`outer_model_obj_id` exists, or errors out.
            try:
                User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse(
                    {"message": f"no user with user_id={outer_model_obj_id}"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            kind_of_account = buyer_or_seller_id_col_name.split("_")[0]

            # Tests whether a
            # `buyer_or_seller_account_class._meta.db_table` row with
            # the column `buyer_or_seller_id_col_name` value (ie. the
            # primary key) equal to `inner_model_obj_id`, or errors out.
            try:
                buyer_or_seller_account = buyer_or_seller_class.objects.get(
                    **{buyer_or_seller_id_col_name: inner_model_obj_id}
                )
            except buyer_or_seller_class.DoesNotExist:
                return JsonResponse(
                    {
                        "message": f"no {kind_of_account} account with "
                        + f"{buyer_or_seller_id_col_name}={inner_model_obj_id}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Testing for valid JSON or erroring out.
            try:
                json_content = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse(
                    {"message": "JSON did not parse"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Testing for valid arguments (in the JSON object) or
            # erroring out.
            try:
                json_content = validate_input(
                    to_buy_or_to_sell_listing_class, json_content, all_nullable=True
                )
            except ValueError as exception:
                return JsonResponse(
                    {"message": exception.args[0]}, status=status.HTTP_400_BAD_REQUEST
                )

            # The input properties are album_id and the price value.
            # Both are required.
            if buyer_or_seller_class is BuyerAccount:
                keys_required = {"max_accepting_price", "album_id"}
            else:
                keys_required = {"asking_price", "album_id"}
            keys_found = set(json_content.keys())

            # If either isn't found, error out.
            diff = keys_required - keys_found
            if diff:
                prop_expr = ", ".join(f"'{prop}'" for prop in diff)
                return JsonResponse(
                    {
                        "message": f"json object missing required propert"
                        + ("ies" if len(diff) > 1 else "y")
                        + f": {prop_expr}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # If any other property is found in the input, error out.
            diff = keys_found - keys_required
            if diff:
                prop_expr = ", ".join(f"'{prop}'" for prop in diff)
                return JsonResponse(
                    {
                        "message": f"unexpected propert"
                        + ("ies" if len(diff) > 1 else "y")
                        + f" in input: {prop_expr}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Tests for the unlikely case where a price was specified
            # with more than 2 decimal places. If the input is trying to
            # refer to fractions of a penny, error out.
            pricing_key = (
                "max_accepting_price"
                if buyer_or_seller_class is BuyerAccount
                else "asking_price"
            )
            pricing_value = json_content[pricing_key]
            if len(pricing_value.split(".")[1]) > 2:
                return JsonResponse(
                    {
                        "message": f"error in input, property "
                        + f"'{pricing_key}': must have only two decimal "
                        + "places"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            new_args = json_content.copy()

            # This handles a bug where attempting to save a new model
            # class object yields an IntegrityError that claims a
            # pre-existing primary key column value was used. This
            # when no primary key column value was set. (This bug is
            # likely in pytest-django, not psycopg2.) This workaround
            # pre-determines the next primary key column value.
            if to_buy_or_to_sell_listing_class is ToBuyListing:
                listing_id_col_name = "to_buy_listing_id"
            else:
                listing_id_col_name = "to_sell_listing_id"

            max_listing_id = max(
                getattr(listing, listing_id_col_name)
                for listing in to_buy_or_to_sell_listing_class.objects.filter()
            )
            new_args[listing_id_col_name] = max_listing_id + 1
            new_args["date_posted"] = date.today()

            # Create the listing and save it.
            listing = to_buy_or_to_sell_listing_class(**new_args)
            setattr(
                listing,
                buyer_or_seller_id_col_name,
                getattr(buyer_or_seller_account, buyer_or_seller_id_col_name),
            )
            listing.save()
            return JsonResponse(listing.serialize(), status=status.HTTP_200_OK)

        return func_dispatch(
            (
                _buyer_seller_all_get,
                _buyer_seller_all_post,
            ),
            request,
        )

    # END closure

    return buyer_seller_all_closure


# Handles requests of the form "GET,PATCH,DELETE
# /users/<user_id>/(buyer|seller)_account/<(buyer|seller)_id>/listings/<
# listing_id>"
def buyer_seller_listing_defclo(
    buyer_or_seller_class,
    buyer_or_seller_id_col_name,
    to_buy_or_to_sell_listing_class,
    to_buy_or_to_sell_listing_id_col_name,
):

    # BEGIN closure
    @api_view(["GET", "PATCH", "DELETE"])
    def buyer_seller_listing_closure(
        request, outer_model_obj_id, inner_model_obj_id, third_model_obj_id
    ):

        # Handles GET requests specifying a user id, a buyer
        # or seller id, and a listing id. For example, GET
        # /users/<user_id>/buyer_account/<buyer_id>/listings/<to_buy_lis
        # ting_id> would return the listing.
        def _buyer_seller_listing_get():

            # Tests whether a matching user with
            # user_id=`outer_model_obj_id` exists, or errors out.
            try:
                User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse(
                    {"message": f"no user with user_id={outer_model_obj_id}"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Tests whether a
            # `buyer_or_seller_account_class._meta.db_table` row with
            # the column `buyer_or_seller_id_col_name` value (ie. the
            # primary key) equal to `inner_model_obj_id` exists, or
            # errors out.
            kind_of_account = buyer_or_seller_id_col_name.split("_")[0]
            try:
                buyer_or_seller_class.objects.get(
                    **{buyer_or_seller_id_col_name: inner_model_obj_id}
                )
            except buyer_or_seller_class.DoesNotExist:
                return JsonResponse(
                    {
                        "message": f"no {kind_of_account} account with "
                        + f"{buyer_or_seller_id_col_name}={inner_model_obj_id}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Tests whether a
            # `to_buy_or_to_sell_listing_class._meta.db_table` row
            # with the column `to_buy_or_to_sell_listing_id_col_name`
            # value (ie. the primary key) equal to `third_model_obj_id`
            # exists, or errors out.
            kind_of_listing = (
                "to-buy listing"
                if buyer_or_seller_class is BuyerAccount
                else "to-sell listing"
            )
            try:
                listing = to_buy_or_to_sell_listing_class.objects.get(
                    **{to_buy_or_to_sell_listing_id_col_name: third_model_obj_id}
                )
            except to_buy_or_to_sell_listing_class.DoesNotExist:
                return JsonResponse(
                    {
                        "message": f"no {kind_of_listing} with "
                        + f"{to_buy_or_to_sell_listing_id_col_name}="
                        + str(third_model_obj_id)
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Return the listing object, serialized.
            return JsonResponse(
                listing.serialize(), status=status.HTTP_200_OK, safe=False
            )

        # Handles PATCH requests specifying a user id, a buyer or
        # seller id, and a listing id. For example, PATCH {json}
        # /users/<user_id>/buyer_account/<buyer_id>/listings/<to_buy_lis
        # ting_id> would update the listing.
        def _buyer_seller_listing_patch():

            # Tests whether a matching user with
            # user_id=`outer_model_obj_id` exists, or errors out.
            try:
                User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse(
                    {"message": f"no user with user_id={outer_model_obj_id}"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Tests whether a
            # `buyer_or_seller_account_class._meta.db_table` row with
            # the column `buyer_or_seller_id_col_name` value (ie. the
            # primary key) equal to `inner_model_obj_id`, or errors out.
            kind_of_account = buyer_or_seller_id_col_name.split("_")[0]
            try:
                buyer_or_seller_class.objects.get(
                    **{buyer_or_seller_id_col_name: inner_model_obj_id}
                )
            except buyer_or_seller_class.DoesNotExist:
                return JsonResponse(
                    {
                        "message": f"no {kind_of_account} account with "
                        + f"{buyer_or_seller_id_col_name}={inner_model_obj_id}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Tests whether a
            # `to_buy_or_to_sell_listing_class._meta.db_table` row
            # with the column `to_buy_or_to_sell_listing_id_col_name`
            # value (ie. the primary key) equal to `third_model_obj_id`
            # exists, or errors out.
            kind_of_listing = (
                "to-buy listing"
                if buyer_or_seller_class is BuyerAccount
                else "to-sell listing"
            )
            try:
                listing = to_buy_or_to_sell_listing_class.objects.get(
                    **{to_buy_or_to_sell_listing_id_col_name: third_model_obj_id}
                )
            except to_buy_or_to_sell_listing_class.DoesNotExist:
                return JsonResponse(
                    {
                        "message": f"no {kind_of_listing} with "
                        + f"{to_buy_or_to_sell_listing_id_col_name}={third_model_obj_id}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            # Validating input.
            result = validate_post_request(
                request, to_buy_or_to_sell_listing_class, all_nullable=True
            )
            if isinstance(result, JsonResponse):
                return result
            json_content = result
            # Testing for non-empty JSON or erroring out.
            if not len(json_content):
                return JsonResponse(
                    {"message": "PATCH request submitted with empty JSON object"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Updating the object and saving it.
            for column in json_content:
                setattr(listing, column, json_content[column])
            listing.save()
            return JsonResponse(listing.serialize(), status=status.HTTP_200_OK)

        # Handles DELETE requests specifying a user id, a buyer
        # or seller id, and a listing id. For example, DELETE
        # /users/<user_id>/buyer_account/<buyer_id>/listings/<to_buy_lis
        # ting_id> would delete the listing.
        def _buyer_seller_listing_delete():

            # Tests whether a matching user with
            # user_id=`outer_model_obj_id` exists, or errors out.
            try:
                User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse(
                    {"message": f"no user with user_id={outer_model_obj_id}"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Tests whether a
            # `buyer_or_seller_account_class._meta.db_table` row with
            # the column `buyer_or_seller_id_col_name` value (ie. the
            # primary key) equal to `inner_model_obj_id`, or errors out.
            kind_of_account = buyer_or_seller_id_col_name.split("_")[0]
            try:
                buyer_or_seller_class.objects.get(
                    **{buyer_or_seller_id_col_name: inner_model_obj_id}
                )
            except buyer_or_seller_class.DoesNotExist:
                return JsonResponse(
                    {
                        "message": f"no {kind_of_account} account with "
                        + f"{buyer_or_seller_id_col_name}={inner_model_obj_id}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Tests whether a
            # `to_buy_or_to_sell_listing_class._meta.db_table` row
            # with the column `to_buy_or_to_sell_listing_id_col_name`
            # value (ie. the primary key) equal to `third_model_obj_id`
            # exists, or errors out.
            kind_of_listing = (
                "to-buy listing"
                if buyer_or_seller_class is BuyerAccount
                else "to-sell listing"
            )
            try:
                listing = to_buy_or_to_sell_listing_class.objects.get(
                    **{to_buy_or_to_sell_listing_id_col_name: third_model_obj_id}
                )
            except to_buy_or_to_sell_listing_class.DoesNotExist:
                return JsonResponse(
                    {
                        "message": f"no {kind_of_listing} with "
                        + f"{to_buy_or_to_sell_listing_id_col_name}="
                        + str(third_model_obj_id)
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Deleting the listing.
            listing.delete()
            return JsonResponse(
                {
                    "message": f"{kind_of_listing} with "
                    + f"{to_buy_or_to_sell_listing_id_col_name}="
                    + f"{third_model_obj_id} deleted"
                },
                status=status.HTTP_200_OK,
            )

        return func_dispatch(
            (
                _buyer_seller_listing_get,
                _buyer_seller_listing_patch,
                _buyer_seller_listing_delete,
            ),
            request,
        )

    # END closure

    return buyer_seller_listing_closure

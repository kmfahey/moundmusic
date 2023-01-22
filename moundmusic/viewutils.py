#!/usr/bin/python3

import json

from datetime import date

from django.http import HttpResponse
from django.http.response import JsonResponse

from rest_framework import status
from rest_framework.decorators import api_view

from users.models import User, BuyerAccount

def validate_input(model_class, input_argd, all_nullable=False):
    validatedDict = dict()
    diff = set(input_argd.keys()) - set(model_class.__columns__)
    if diff:
        diff_expr = ', '.join(f"'{key}'" for key in diff)
        raise ValueError(f'unexpected propert{"ies" if len(diff) > 1 else "y"} in input: {diff_expr}')
    for column, value in input_argd.items():
        column_type = model_class.__columns__[column]
        if value is None:
            if not all_nullable and column not in model_class.__nullable_cols__:
                raise ValueError(f"value for '{column}' is null and column not nullable")
        elif column_type is int:
            try:
                value = int(value)
            except ValueError:
                raise ValueError(f"value for '{column}' isn't an integer: {value}")
            if value <= 0:
                raise ValueError(f"value for '{column}' isn't greater than 0: {value}")
        elif column_type is float:
            try:
                value = float(value)
            except ValueError:
                raise ValueError(f"value for '{column}' isn't a decimal: {value}")
            if value <= 0:
                raise ValueError(f"value for '{column}' isn't greater than 0: {value}")
        elif column_type is str and not len(value):
            raise ValueError(f"value for '{column}' is a string of zero length")
        elif column_type is date:
            try:
                value = date.fromisoformat(value)
            except ValueError:
                raise ValueError(f"value for '{column}' isn't in format YYYY-MM-DD and column is a DATE")
        elif isinstance(column_type, tuple):
            if value not in column_type:
                enum_expr = ', '.join(f"'{option}'" for option in column_type[:-1]) + f" or '{column_type[-1]}'"
                raise ValueError(f"value for '{column}' not one of {enum_expr} and column is an ENUM type")
        validatedDict[column] = value
    return validatedDict


def dispatch_funcs_by_method(functions, request):
    dispatch_table = dict()
    for function in functions:
        func_name = function.__name__
        _, method = func_name.rsplit('_', 1)
        dispatch_table[method] = function
    method = request.method
    if method in dispatch_table:
        return dispatch_table[method]()
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


def validate_post_request(request, model_class, all_nullable=False):
    try:
        posted_json = json.loads(request.body)
    except JSONDecodeError:
        return JsonResponse({'message': 'JSON did not parse'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        validated_args = validate_input(model_class, posted_json, all_nullable=all_nullable)
    except ValueError as exception:
        return JsonResponse({'message': exception.args[0]}, status=status.HTTP_400_BAD_REQUEST)
    return validated_args


def validate_patch_request(request, model_class, model_id_attr_name, model_id_attr_val):
    try:
        model_instance = model_class.objects.get(**{model_id_attr_name: model_id_attr_val})
    except model_class.DoesNotExist:
        return JsonResponse({'message': f'no {model_class.__name__.lower()} with '
                                        f'{model_id_attr_name}={model_id_attr_val}'},
                            status=status.HTTP_404_NOT_FOUND)
    try:
        posted_json = json.loads(request.body)
    except JSONDecodeError as exception:
        return JsonResponse({'message': exception.args[0]}, status=status.HTTP_400_BAD_REQUEST)
    if not len(posted_json):
        return JsonResponse({'message': 'empty JSON object'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        validated_input = validate_input(model_class, posted_json, all_nullable=True)
    except ValueError as exception:
        return JsonResponse({'message': exception.args[0]}, status=status.HTTP_400_BAD_REQUEST)
    return model_instance, validated_input


def validate_bridged_table_column_value_pair(left_model_class, left_model_attr_name, left_model_attr_value,
                                             right_model_class, right_model_attr_name, right_model_attr_value,
                                             bridge_model_class):
    try:
        left_model_obj = left_model_class.objects.get(**{left_model_attr_name: left_model_attr_value})
    except left_model_class.DoesNotExist:
        return JsonResponse({'message': f'no {left_model_class.__name__.lower()} with '
                                        f'{left_model_attr_name}={left_model_attr_value}'},
                            status=status.HTTP_404_NOT_FOUND)
    try:
        right_model_obj = right_model_class.objects.get(**{right_model_attr_name: right_model_attr_value})
    except right_model_class.DoesNotExist:
        return JsonResponse({'message': f'no {right_model_class.__name__.lower()} with '
                                        f'{right_model_attr_name}={right_model_attr_value}'},
                            status=status.HTTP_404_NOT_FOUND)
    try:
        bridge_row = bridge_model_class.objects.get(**{left_model_attr_name: left_model_attr_value,
                                                       right_model_attr_name: right_model_attr_value})
    except bridge_model_class.DoesNotExist:
        return JsonResponse({'message': f'{left_model_class.__name__.lower()} with '
                                        f'{left_model_attr_name}={left_model_attr_value} not associated with '
                                        f'{right_model_class.__name__.lower()} with '
                                        f'{right_model_attr_name}={right_model_attr_value}'},
                            status=status.HTTP_404_NOT_FOUND)
    return left_model_obj, right_model_obj, bridge_row


def define_GET_POST_index_closure(model_class, model_id_attr_name):
    @api_view(['GET', 'POST'])
    def index(request):

        def _index_GET():
            return JsonResponse([model_obj.serialize() for model_obj in model_class.objects.all()],
                                status=status.HTTP_200_OK, safe=False)

        def _index_POST():
            result = validate_post_request(request, model_class)
            if isinstance(result, JsonResponse):
                return result
            else:
                validated_args = result
            if model_id_attr_name in validated_args:
                return JsonResponse({'message': f'a new {model_class.__name__.lower()} object '
                                                f'must not have a {model_id_attr_name} value'},
                                    status=status.HTTP_400_BAD_REQUEST)
            max_id_attr_value = max(getattr(row_obj, model_id_attr_name) for row_obj in model_class.objects.filter())
            new_args = validated_args.copy()
            new_args[model_id_attr_name] = max_id_attr_value + 1
            new_model_obj = model_class(**new_args)
            new_model_obj.save()
            return JsonResponse(new_model_obj.serialize(), status=status.HTTP_201_CREATED)

        return dispatch_funcs_by_method((_index_GET, _index_POST), request)

    return index


def define_single_model_GET_PATCH_DELETE_closure(model_class, model_id_attr_name):
    @api_view(['GET', 'PATCH', 'DELETE'])
    def single_model(request, model_obj_id):

        def _single_model_GET():
            try:
                model_obj = model_class.objects.get(**{model_id_attr_name: model_obj_id})
            except model_class.DoesNotExist:
                return JsonResponse({'message': f'no {model_class.__name__.lower()} '
                                                f'with {model_id_attr_name}={model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            return JsonResponse(model_obj.serialize(), status=status.HTTP_200_OK)

        def _single_model_PATCH():
            retval = validate_patch_request(request, model_class, model_id_attr_name, model_obj_id)
            if isinstance(retval, JsonResponse):
                return retval
            else:
                model_obj, validated_input = retval
            if model_id_attr_name in validated_input:
                return JsonResponse({'message': f'an updated {model_class.__name__.lower()} object '
                                                f'must not have a {model_id_attr_name} value'},
                                    status=status.HTTP_400_BAD_REQUEST)
            for column, column_value in validated_input.items():
                setattr(model_obj, column, column_value)
            model_obj.save()
            return JsonResponse(model_obj.serialize(), status=status.HTTP_200_OK)

        def _single_model_DELETE():
            try:
                model_obj = model_class.objects.get(**{model_id_attr_name: model_obj_id})
            except model_class.DoesNotExist:
                return JsonResponse({'message': f'no {model_class.__name__.lower()} '
                                                f'with {model_id_attr_name}={model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            model_obj.delete()
            return JsonResponse({'message': f'{model_class.__name__.lower()} '
                                            f'with {model_id_attr_name}={model_obj_id} deleted'},
                                status=status.HTTP_200_OK)

        return dispatch_funcs_by_method((_single_model_GET, _single_model_PATCH, _single_model_DELETE), request)

    return single_model


def define_single_outer_model_all_of_inner_model_GET_POST_closure(outer_model_class, outer_model_id_attr_name,
                                                                  inner_model_class, inner_model_id_attr_name,
                                                                  bridge_class):
    @api_view(['GET', 'POST'])
    def single_outer_model_all_of_inner_model(request, outer_model_obj_id):

        def _single_outer_model_all_of_inner_model_GET():
            try:
                outer_model_class.objects.get(**{outer_model_id_attr_name: outer_model_obj_id})
            except outer_model_class.DoesNotExist:
                return JsonResponse({'message': f'no {outer_model_class.__name__.lower()} with '
                                                f'{outer_model_id_attr_name}={outer_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            bridge_rows = bridge_class.objects.filter(**{outer_model_id_attr_name: outer_model_obj_id})
            return_list = [inner_model_class.objects.get(**{inner_model_id_attr_name:
                                                            getattr(bridge_row, inner_model_id_attr_name)}).serialize()
                           for bridge_row in bridge_rows]
            return JsonResponse(return_list, status=status.HTTP_200_OK, safe=False)

        def _single_outer_model_all_of_inner_model_POST():
            try:
                outer_model_class.objects.get(**{outer_model_id_attr_name: outer_model_obj_id})
            except outer_model_class.DoesNotExist:
                return JsonResponse({'message': f'no {outer_model_class.__name__.lower()} '
                                                f'with {outer_model_id_attr_name}={outer_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            try:
                posted_json = json.loads(request.body)
            except JSONDecodeError as exception:
                return JsonResponse({'message': exception.args[0]}, status=status.HTTP_400_BAD_REQUEST)
            diff = set(posted_json.keys()) - set((inner_model_id_attr_name,))
            if diff:
                prop_expr = ', '.join(f"'{property}'" for property in diff)
                return JsonResponse({'message': f'unexpected propert{"ies" if len(diff) > 1 else "y"} '
                                                f'in input: {prop_expr}'},
                                    status=status.HTTP_400_BAD_REQUEST)
            inner_model_obj_id = posted_json[inner_model_id_attr_name]
            try:
                inner_model_obj = inner_model_class.objects.get(**{inner_model_id_attr_name: inner_model_obj_id})
            except inner_model_class.DoesNotExist:
                return JsonResponse({'message': f'no {inner_model_class.__name__.lower()} '
                                                f'with {inner_model_id_attr_name}={inner_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            try:
                bridge_row = bridge_class.objects.get(**{outer_model_id_attr_name: outer_model_obj_id,
                                                         inner_model_id_attr_name: inner_model_obj_id})
            except bridge_class.DoesNotExist:
                pass
            else:
                return JsonResponse({'message': f'association between {outer_model_class.__name__.lower()} with '
                                                f'{outer_model_id_attr_name}={outer_model_obj_id} '
                                                f'and {inner_model_class.__name__.lower()} with '
                                                f'{inner_model_id_attr_name}={inner_model_obj_id} '
                                                 'already exists'},
                                    status=status.HTTP_400_BAD_REQUEST)
            bridge_table_name = bridge_class._meta.db_table
            bridge_table_id_col = f"{bridge_table_name}_id"
            max_bridge_row_id = max(getattr(bridge_row, bridge_table_id_col) for bridge_row in bridge_class.objects.filter())
            bridge_row = bridge_class(**{bridge_table_id_col: max_bridge_row_id + 1,
                                         outer_model_id_attr_name: outer_model_obj_id,
                                         inner_model_id_attr_name: inner_model_obj_id})
            bridge_row.save()
            return JsonResponse(inner_model_obj.serialize(), status=status.HTTP_200_OK)

        return dispatch_funcs_by_method((_single_outer_model_all_of_inner_model_GET,
                                          _single_outer_model_all_of_inner_model_POST), request)

    return single_outer_model_all_of_inner_model

def define_single_outer_model_single_inner_model_GET_DELETE_closure(outer_model_class, outer_model_id_attr_name,
                                                                    inner_model_class, inner_model_id_attr_name,
                                                                    bridge_class):
    @api_view(['GET', 'DELETE'])
    def single_outer_model_single_inner_model(request, outer_model_obj_id, inner_model_obj_id):

        def _single_outer_model_single_inner_model_GET():
            result = validate_bridged_table_column_value_pair(outer_model_class,
                                                              outer_model_id_attr_name,
                                                              outer_model_obj_id,
                                                              inner_model_class,
                                                              inner_model_id_attr_name,
                                                              inner_model_obj_id,
                                                              bridge_class)
            if isinstance(result, JsonResponse):
                return result
            else:
                _, inner_model, _ = result
            return JsonResponse(inner_model.serialize(), status=status.HTTP_200_OK)

        def _single_outer_model_single_inner_model_DELETE():
            result = validate_bridged_table_column_value_pair(outer_model_class,
                                                              outer_model_id_attr_name,
                                                              outer_model_obj_id,
                                                              inner_model_class,
                                                              inner_model_id_attr_name,
                                                              inner_model_obj_id,
                                                              bridge_class)
            if isinstance(result, JsonResponse):
                return result
            else:
                _, _, bridge_row = result
            bridge_row.delete()
            return JsonResponse({'message': f'association between {outer_model_class.__name__.lower()} with '
                                            f'{outer_model_id_attr_name}={outer_model_obj_id} '
                                            f'and {inner_model_class.__name__.lower()} with '
                                            f'{inner_model_id_attr_name}={inner_model_obj_id} deleted'},
                                status=status.HTTP_200_OK)

        return dispatch_funcs_by_method((_single_outer_model_single_inner_model_GET,
                                          _single_outer_model_single_inner_model_DELETE), request)

    return single_outer_model_single_inner_model


def define_single_user_any_buyer_or_seller_account_GET_POST_closure(buyer_or_seller_account_class, buyer_or_seller_id_col_name):
    @api_view(['GET', 'POST'])
    def single_user_any_buyer_or_seller_account(request, outer_model_obj_id):
        def _single_user_any_buyer_or_seller_account_GET():
            try:
                user = User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse({'message': f'no user with user_id={outer_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            if getattr(user, buyer_or_seller_id_col_name) is None:
                return JsonResponse({"message": f"user with user_id={outer_model_obj_id} has "
                                                 "no associated buyer account"},
                                    content_type="application/json", status=status.HTTP_404_NOT_FOUND)
            try:
                buyer_account = buyer_or_seller_account_class.objects.get(user_id=outer_model_obj_id)
            except buyer_or_seller_account_class.DoesNotExist:
                return JsonResponse({"message": f"user with user_id={outer_model_obj_id} has "
                                                 "no associated buyer account"},
                                    content_type="application/json", status=status.HTTP_404_NOT_FOUND)
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
                return JsonResponse({"message": f"user with user_id={outer_model_obj_id} already has "
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


def define_single_user_single_buyer_or_seller_account_GET_DELETE_closure(buyer_or_seller_account_class,
                                                                         buyer_or_seller_id_col_name):

    @api_view(['GET', 'DELETE'])
    def single_user_single_buyer_or_seller_account(request, outer_model_obj_id, inner_model_obj_id):
        def _single_user_single_buyer_or_seller_account_GET():
            try:
                User.objects.get(user_id=outer_model_obj_id)
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
            return JsonResponse({"message": f"{kind_of_account} account with "
                                            f"{buyer_or_seller_id_col_name}={inner_model_obj_id} associated with "
                                            f"user with user_id={outer_model_obj_id} disassociated and deleted"},
                                status=status.HTTP_200_OK)

        return dispatch_funcs_by_method((_single_user_single_buyer_or_seller_account_GET,
                                         _single_user_single_buyer_or_seller_account_DELETE), request)

    return single_user_single_buyer_or_seller_account


def define_single_user_single_buyer_or_seller_account_any_listing_GET_POST_closure(buyer_or_seller_class,
                                                                                   buyer_or_seller_id_col_name,
                                                                                   to_buy_or_to_sell_listing_class):

    @api_view(['GET', 'POST'])
    def single_user_single_buyer_or_seller_account_any_listing(request, outer_model_obj_id, inner_model_obj_id):
        def _single_user_single_buyer_or_seller_account_any_listing_GET():
            try:
                User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse({'message': f'no user with user_id={outer_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            kind_of_account = buyer_or_seller_id_col_name.split('_')[0]
            try:
                buyer_or_seller_class.objects.get(**{buyer_or_seller_id_col_name: inner_model_obj_id})
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
                User.objects.get(user_id=outer_model_obj_id)
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
                json_content = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({'message': 'JSON did not parse'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                json_content = validate_input(to_buy_or_to_sell_listing_class, json_content, all_nullable=True)
            except ValueError as exception:
                return JsonResponse({'message': exception.args[0]}, status=status.HTTP_400_BAD_REQUEST)
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


def define_single_user_single_buyer_or_seller_account_single_listing_GET_PATCH_DELETE_closure(buyer_or_seller_class,
                                                                                              buyer_or_seller_id_col_name,
                                                                                              to_buy_or_to_sell_listing_class,
                                                                                              to_buy_or_to_sell_listing_id_col_name):
    @api_view(['GET', 'PATCH', 'DELETE'])
    def single_user_single_buyer_or_seller_account_single_listing(request, outer_model_obj_id, inner_model_obj_id,
                                                                  third_model_obj_id):

        def _single_user_single_buyer_or_seller_account_single_listing_GET():
            try:
                User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse({'message': f'no user with user_id={outer_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            kind_of_account = buyer_or_seller_id_col_name.split('_')[0]
            try:
                buyer_or_seller_class.objects.get(**{buyer_or_seller_id_col_name: inner_model_obj_id})
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

        def _single_user_single_buyer_or_seller_account_single_listing_PATCH():
            try:
                User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse({'message': f'no user with user_id={outer_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            kind_of_account = buyer_or_seller_id_col_name.split('_')[0]
            try:
                buyer_or_seller_class.objects.get(**{buyer_or_seller_id_col_name: inner_model_obj_id})
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
            result = validate_post_request(request, to_buy_or_to_sell_listing_class, all_nullable=True)
            if isinstance(result, JsonResponse):
                return result
            json_content = result
            if not len(json_content):
                return JsonResponse({'message': f'PATCH request submitted with empty JSON object'},
                                    status=status.HTTP_400_BAD_REQUEST)
            for column in json_content:
                setattr(listing, column, json_content[column])
            listing.save()
            return JsonResponse(listing.serialize(), status=status.HTTP_200_OK)

        def _single_user_single_buyer_or_seller_account_single_listing_DELETE():
            try:
                User.objects.get(user_id=outer_model_obj_id)
            except User.DoesNotExist:
                return JsonResponse({'message': f'no user with user_id={outer_model_obj_id}'},
                                    status=status.HTTP_404_NOT_FOUND)
            kind_of_account = buyer_or_seller_id_col_name.split('_')[0]
            try:
                buyer_or_seller_class.objects.get(**{buyer_or_seller_id_col_name: inner_model_obj_id})
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
            return JsonResponse({"message": f"{kind_of_listing} with "
                                            f"{to_buy_or_to_sell_listing_id_col_name}={third_model_obj_id} deleted"},
                                status=status.HTTP_200_OK)


        return dispatch_funcs_by_method((_single_user_single_buyer_or_seller_account_single_listing_GET,
                                         _single_user_single_buyer_or_seller_account_single_listing_PATCH,
                                         _single_user_single_buyer_or_seller_account_single_listing_DELETE), request)

    return single_user_single_buyer_or_seller_account_single_listing


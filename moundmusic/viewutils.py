#!/usr/bin/python3

from datetime import date

from django.http import HttpResponse
from django.http.response import JsonResponse

from json.decoder import JSONDecodeError
from json import loads as parse_json

from rest_framework import status
from rest_framework.decorators import api_view


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
        posted_json = parse_json(request.body)
    except JSONDecodeError:
        return JsonResponse({'message':'JSON did not parse'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        validated_args = validate_input(model_class, posted_json, all_nullable=all_nullable)
    except ValueError as exception:
        return JsonResponse({'message':exception.args[0]}, status=status.HTTP_400_BAD_REQUEST)
    return validated_args


def validate_patch_request(request, model_class, model_id_attr_name, model_id_attr_val):
    try:
        model_instance = model_class.objects.get(**{model_id_attr_name: model_id_attr_val})
    except model_class.DoesNotExist:
        return JsonResponse({'message':f'no {model_class.__name__.lower()} with '
                                       f'{model_id_attr_name}={model_id_attr_val}'},
                            status=status.HTTP_404_NOT_FOUND)
    try:
        posted_json = parse_json(request.body)
    except JSONDecodeError as exception:
        return JsonResponse({'message':exception.args[0]}, status=status.HTTP_400_BAD_REQUEST)
    if not len(posted_json):
        return JsonResponse({'message':'empty JSON object'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        validated_input = validate_input(model_class, posted_json, all_nullable=True)
    except ValueError as exception:
        return JsonResponse({'message':exception.args[0]}, status=status.HTTP_400_BAD_REQUEST)
    return model_instance, validated_input


def validate_bridged_table_column_value_pair(left_model_class, left_model_attr_name, left_model_attr_value,
                                             right_model_class, right_model_attr_name, right_model_attr_value,
                                             bridge_model_class):
    try:
        left_model_obj = left_model_class.objects.get(**{left_model_attr_name:left_model_attr_value})
    except left_model_class.DoesNotExist:
        return JsonResponse({'message':f'no {left_model_class.__name__.lower()} with '
                                       f'{left_model_attr_name}={left_model_attr_value}'},
                            status=status.HTTP_404_NOT_FOUND)
    try:
        right_model_obj = right_model_class.objects.get(**{right_model_attr_name:right_model_attr_value})
    except right_model_class.DoesNotExist:
        return JsonResponse({'message':f'no {right_model_class.__name__.lower()} with '
                                       f'{right_model_attr_name}={right_model_attr_value}'},
                            status=status.HTTP_404_NOT_FOUND)
    try:
        bridge_row = bridge_model_class.objects.get(**{left_model_attr_name:left_model_attr_value,
                                                       right_model_attr_name:right_model_attr_value})
    except bridge_model_class.DoesNotExist:
        return JsonResponse({'message':f'{left_model_class.__name__.lower()} with '
                                       f'{left_model_attr_name}={left_model_attr_value} not associated with '
                                       f'{right_model_class.__name__.lower()} with '
                                       f'{right_model_attr_name}={right_model_attr_value}'},
                            status=status.HTTP_404_NOT_FOUND)
    return left_model_obj, right_model_obj, bridge_row


def define_GET_POST_index_closure(model_class, model_obj_attr_name):
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
            if model_obj_attr_name in validated_args:
                return JsonResponse({'message':f'a new {model_class.__name__.lower()} object '
                                               f'must not have a {model_obj_attr_name} value'},
                                    status=status.HTTP_400_BAD_REQUEST)
            new_model_obj = model_class(**validated_args)
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
                posted_json = parse_json(request.body)
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
            bridge_row = bridge_class(**{outer_model_id_attr_name: outer_model_obj_id,
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


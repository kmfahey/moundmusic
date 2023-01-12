#!/usr/bin/python3

from datetime import date

from django.http import HttpResponse
from django.http.response import JsonResponse

from json.decoder import JSONDecodeError
from json import loads as parse_json

from rest_framework import status


def validate_input(model_class, input_argd, all_nullable=False):
    validatedDict = dict()
    diff = set(input_argd.keys()) - set(model_class.__columns__)
    if diff:
        diff_expr = ', '.join(f"'{key}'" for key in diff)
        raise ValueError(f'unexpected propert{"ies" if len(diff) > 1 else "y"} in input: {diff_expr}')
    for column, value in input_argd.items():
        column_type = model_class.__columns__[column]
        if value is None and not all_nullable and column not in model_class.__nullable_cols__ \
                and column not in override_cols:
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



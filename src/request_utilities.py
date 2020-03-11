"""
"""
from functools import wraps

from flask import request

from .exceptions import NoSuchKey

def _is_empty(string_):
    return string_ == None or string_ == ''

def get_field(request_body, field_name):
    return request_body.get(field_name, None)

def get_required_field(request_body, field_name):
    field_value = get_field(request_body, field_name)
    if _is_empty(field_value):
        raise NoSuchKey(field_name, request_body)
    return field_value

def request_is_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return '', 400
        return f(*args, **kwargs)
    return decorated_function

def get_boolean_field(request_body, field_name):
    field_value = get_field(request_body, field_name)
    return field_value in {True, 'True', 'true', 1, '1'}
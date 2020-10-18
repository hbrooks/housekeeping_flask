import logging

from ..exceptions import HouseKeepingBaseException


LOG = logging.getLogger(__name__)

class ContentType_400(HouseKeepingBaseException):
    def __init__(self):
        super().__init__(400, "Use 'content-type: application/json'.", None)


class MissingField_400(HouseKeepingBaseException):
    def __init__(self, field_name, object_expected_to_contain_field):
        super().__init__(
            400,
            '"{}" is missing from this key set: {}'.format(field_name, ', '.join(object_expected_to_contain_field.keys())),
            None
        )

def get_json(request):
    """
    If a supplied Flask request object is parsable as json, return a dict of the request body.
    If not, raise a HouseKeeping exception.
    """
    if not request.is_json:
        raise ContentType_400
    body = request.get_json(silent=True)
    return {} if body == None else body

def get_field(d, field_name):
    """
    Returns a field from a dictionary. Raises if it doesn't exist.
    """
    field_value = d.get(field_name, None)
    if field_value == None:
        raise MissingField_400(field_name, d)
    return field_value

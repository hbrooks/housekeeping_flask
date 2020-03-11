class HouseKeepingBaseException(Exception):
    def __init__(self, status_code, description, details):
        self.description = description
        self.status_code = status_code
        self.details = details

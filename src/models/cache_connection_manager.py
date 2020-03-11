import logging

from redis import Redis


LOG = logging.getLogger(__name__)


class CacheConnectionManager:
    # TODO: Extend something like ExternalDependencyConnection that mandates that validate_connection() and self.cache exists.

    def __init__(self, connection_details):
        host_name = connection_details['host_name']
        port = connection_details['port']
        self.cache = Redis(
            host=host_name,
            port=port,
        )
    
    def get_connection(self):
        return self.cache
    
    def validate_connection(self):
        self.get_connection().ping()
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy_session import flask_scoped_session
from flask import current_app

LOG = logging.getLogger(__name__)


class DatabaseConnectionManager:
    # TODO: Extend something like ExternalDependencyConnection that mandates that validate_connection() and self.cache exists.

    def __init__(self, connection_details):
        """
        TODO: Change constructor to provide 5 fields explicity, not a dictionary.
        """
        
        self.engine = create_engine(DatabaseConnectionManager.get_connection_string(connection_details))

        session_maker = sessionmaker(bind=self.engine)

        def _get_session():
            return flask_scoped_session(session_maker, current_app)
        self.get_session = _get_session

        def _validate_postgres_distilr_api_flask_internal_connection():
            session = _get_session()
            session.execute('select 1;')
        self.validate_connection = _validate_postgres_distilr_api_flask_internal_connection

    def get_engine(self):
        return self.engine

    @staticmethod
    def get_connection_string(connection_details):
        user = connection_details['MYSQL_USER']
        password = connection_details['MYSQL_ROOT_PASSWORD']
        host_name = connection_details['MYSQL_HOST']
        port = connection_details['MYSQL_PORT']
        db_name = connection_details['MYSQL_DB_NAME']
        return f'mysql+pymysql://{user}:{password}@{host_name}:{port}/{db_name}'

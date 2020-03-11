import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy_session import flask_scoped_session
from flask import current_app

LOG = logging.getLogger(__name__)


class DatabaseConnectionManager:
    # TODO: Extend something like ExternalDependencyConnection that mandates that validate_connection() and self.cache exists.

    def __init__(self, connection_details):
        
        engine = create_engine(DatabaseConnectionManager.get_connection_string('root', 'flamingo', 'mysql_relational_database', '3306', 'distilr_news'))

        session_maker = sessionmaker(bind=engine)

        def _get_session():
            return flask_scoped_session(session_maker, current_app)
        self.get_session = _get_session

        def _validate_postgres_distilr_api_flask_internal_connection():
            session = _get_session()
            session.execute('select 1;')
        self.validate_connection = _validate_postgres_distilr_api_flask_internal_connection


    @staticmethod
    def get_connection_string(db_user, db_pwd, db_host, db_port, db_name):
        return f'mysql+pymysql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}'

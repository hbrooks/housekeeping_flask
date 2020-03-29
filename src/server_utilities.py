import json
import os
import logging

from flask import Flask
from flask_cors import CORS

from flask import current_app
from flask import g
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy_session import flask_scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from .exceptions import HouseKeepingBaseException

LOG = logging.getLogger(__name__)
database_connection_manager = None


def create_dict_from_env_vars(env_vars):
    return {
        field_name: os.environ[field_name] for field_name in env_vars
    }


class HouseKeepingApiServer:

    def __init__(
            self,
            models,
            blueprints,
            build_app_context_function=None,
            before_request_function=None,
            health_check_function=None,
            include_db_clean_endpoint=True):
        self.models = models
        self.blueprints = blueprints
        self.build_app_context_function = build_app_context_function
        self.before_request_function = before_request_function
        self.health_check_function = health_check_function if health_check_function != None else self._get_default_heathCheck_function()
        self.include_db_clean_endpoint = include_db_clean_endpoint

    def _get_default_heathCheck_function(self):
        def _DEFAULT_HEALTH_CHECK_FUNCITON(_):
            return '', 200

    def build_flask_app(self):

        LOG.info("Starting up...")

        app = Flask(__name__)

        CORS(app)
        self._configure_logging()

        if self.build_app_context_function:
            with app.app_context():
                self.build_app_context_function(self)

        if self.before_request_function:
            @app.before_request
            def before_request_function_():
                self.before_request_function(self)

        internal_blueprint = self._build_internal_routes(
            self.health_check_function,
            self.include_db_clean_endpoint
        )
        self.blueprints.add(internal_blueprint)

        # if self.health_check_function:
        #     @app.route(self.HEALTH_CHECK_URI, methods=('GET',))
        #     def health_check_function_():
        #         return self.health_check_function(self)

        # else:
        #     @app.route(self.HEALTH_CHECK_URI, methods=('GET',))
        #     def DEAFULT_HEALTH_CHECK_FUNCITON():
        #         return '', 200

        @app.errorhandler(HouseKeepingBaseException)
        def handle_housekeeping_exceptions(e):
            response_body = {
                "description": e.description,
                'details': e.details
            }
            LOG.error(e.description+': '+json.dumps(e.details))
            return response_body, e.status_code,  {'Content-Type': 'application/json'}

        @app.errorhandler(Exception)
        def handle_exceptions(e):
            response_body = {
                "description": str(e),
            }
            LOG.error('---- {} (500) ----'.format(e.__class__.__name__))
            LOG.exception(e)
            LOG.error('------------------')
            return response_body, 500,  {'Content-Type': 'application/json'}

        for current_blueprint in self.blueprints:
            app.register_blueprint(current_blueprint)

        return app

    def _build_internal_routes(
        self,
            health_check_function,
            include_db_clean_endpoint
        ):
        
        internal_routes_blueprint = Blueprint(
            'internal',
            __name__,
            url_prefix='/internal')

        if include_db_clean_endpoint:
            @internal_routes_blueprint.route("/db/clean", methods=('POST',))
            def clean_database():
                TABLES_TO_TRUNCATE = { # TODO: Customize this for each service.
                    'users',
                    'events',
                    'user_events',
                    'user_activities'
                }
                db = g.session()
                for table in TABLES_TO_TRUNCATE:
                    db.execute('truncate {};'.format(table))
                db.commit()
                
                return '', 200

        @internal_routes_blueprint.route('/healthCheck', methods=('GET',))
        def health_check_function_():
            return health_check_function(self)

        return internal_routes_blueprint

    
    def _configure_logging(self):
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('werkzeug').setLevel(logging.INFO)


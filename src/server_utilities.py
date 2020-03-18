import json
import os
import logging

from flask import Flask
from flask_cors import CORS

from flask import current_app
from flask import g
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

    HEALTH_CHECK_URI = '/healthCheck'

    def __init__(self, models, blueprints, build_app_context_function=None, before_request_function=None, health_check_function=None):
        self.models = models
        self.blueprints = blueprints
        self.build_app_context_function = build_app_context_function
        self.before_request_function = before_request_function
        self.health_check_function = health_check_function

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

        if self.health_check_function:
            @app.route(self.HEALTH_CHECK_URI, methods=('GET',))
            def health_check_function_():
                return self.health_check_function(self)

        else:
            @app.route(self.HEALTH_CHECK_URI, methods=('GET',))
            def DEAFULT_HEALTH_CHECK_FUNCITON():
                return '', 200


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

        for blueprint_ in self.blueprints:
            app.register_blueprint(blueprint_)

        return app


    
    def _configure_logging(self):
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('werkzeug').setLevel(logging.INFO)


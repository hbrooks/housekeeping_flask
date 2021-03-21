import json
import os
import logging

from flask import Flask
from flask_cors import CORS

from flask import current_app
from flask import g
from flask import Blueprint

from .exceptions import HouseKeepingBaseException

LOG = logging.getLogger(__name__)
database_connection_manager = None  # Not needed.


def get_env_var(env_var):
    return os.environ[env_var]


def create_dict_from_env_vars(env_vars):
    return {
        field_name: get_env_var(field_name) for field_name in env_vars
    }


class HouseKeepingApiServer:

    def __init__(
            self,
            models,
            blueprints,
            build_app_context_function=None,
            before_request_function=None,
            health_check_function=None):
        self.models = models
        self.blueprints = blueprints
        self.build_app_context_function = build_app_context_function
        self.before_request_function = before_request_function
        self.health_check_function = self._DEFAULT_HEALTH_CHECK_FUNCTION if health_check_function is None else health_check_function

    def build_flask_app(self):

        LOG.info("Starting up...")

        app = Flask(__name__)

        CORS(app)
        self._configure_logging()

        if self.build_app_context_function:
            with app.app_context():
                self.build_app_context_function()

        if self.before_request_function:
            @app.before_request
            def before_request_function_():
                self.before_request_function()

        internal_blueprint = self._build_internal_routes(
            self.health_check_function)
        self.blueprints.add(internal_blueprint)

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

    def _build_internal_routes(self, health_check_function):

        internal_routes_blueprint = Blueprint(
            'internal',
            __name__,
            url_prefix='/internal')

        @internal_routes_blueprint.route('/healthCheck', methods=('GET',))
        def health_check_function_():
            return health_check_function()

        return internal_routes_blueprint

    def _configure_logging(self):
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('werkzeug').setLevel(logging.INFO)

    def _DEFAULT_HEALTH_CHECK_FUNCTION(self):
        return '', 200

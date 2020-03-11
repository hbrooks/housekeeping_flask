__version__ = (1, 0, 0, "dev")

import os
import logging
import json

from flask import Flask
from flask import g
from flask_cors import CORS

from .exceptions import DistilrBaseException

LOG = logging.getLogger(__name__)

HEALTH_CHECK_URI = '/healthCheck'


def _configure_logging():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('werkzeug').setLevel(logging.INFO)


def build_distilr_api(
    # TODO: Pass application name in so it can be used in log prefix
    blueprints, # Collection of flask Blueprints
    build_distilr_application_context=None, # Built within the Flask app context.
    health_check_function=None, # Called with 1 arg: flask_app
    before_request_function=None): # Called with 1 arg: flask_app

    # logging.getLogger('flask_cors').level = logging.DEBUG

    LOG.info("Startup beggining...")

    app = Flask(__name__)

    CORS(app)
    _configure_logging()

    distilr_application_context = None
    if build_distilr_application_context:
        with app.app_context():
            distilr_application_context = build_distilr_application_context()
    distilr_application_context = {} if distilr_application_context == None else distilr_application_context

    if before_request_function:
        @app.before_request
        def before_request_function_():
            before_request_function(distilr_application_context)

    if health_check_function:
        @app.route(HEALTH_CHECK_URI, methods=('GET',))
        def health_check_function_():
            return health_check_function(g)

    else:
        @app.route(HEALTH_CHECK_URI, methods=('GET',))
        def DEAFULT_HEALTH_CHECK_FUNCITON():
            return '', 200


    @app.errorhandler(DistilrBaseException)
    def handle_distilr_exceptions(e):
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

    for blueprint_ in blueprints:
        app.register_blueprint(blueprint_)

    return app

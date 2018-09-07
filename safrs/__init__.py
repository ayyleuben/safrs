'''
__init__.py
'''
import logging, os, builtins, sys
from flask_swagger_ui import get_swaggerui_blueprint
from flask import Flask, redirect

class SAFRS(object):
    '''This class configures the Flask application to serve SAFRSBase instances

    :param app: a Flask application.
    :param prefix: URL prefix where the swagger should be hosted. Default is '/api'
    :param LOGLEVEL: loglevel configuration variable, values from logging module (0: trace, .. 50: critical)

    '''

    # Config settings
    SAFRS_UNLIMITED = 250
    ENABLE_RELATIONSHIPS = None
    LOGLEVEL = logging.WARNING
    OBJECT_ID_SUFFIX = None
    ENABLE_RELATIONSHIPS = None

    def __new__(cls, app, db, prefix = '/api', **kwargs):
        if not isinstance(app, Flask):
            raise TypeError("'app' should be Flask.")

        cls.app = app
        cls.db = db

        if app.config.get('DEBUG', False):
            cls.LOGLEVEL = logging.DEBUG

        app.url_map.strict_slashes = False
        app.json_encoder = SAFRSJSONEncoder
        # Register the API at /api
        swaggerui_blueprint = get_swaggerui_blueprint(prefix, '/api/swagger.json')
        app.register_blueprint(swaggerui_blueprint, url_prefix= prefix)

        @app.route('/')
        def goto_api():
            return redirect(prefix)

        @app.teardown_appcontext
        def shutdown_session(exception=None):
            '''cfr. http://flask.pocoo.org/docs/0.12/patterns/sqlalchemy/'''
            cls.db.session.remove()        

        for k, v in kwargs.items():
            setattr(cls, k, v)

        for k, v in app.config.items():
            setattr(cls, k, v)

        cls.init_logging(SAFRS.LOGLEVEL)

        return object.__new__(object)

    @classmethod
    def init_logging(cls, loglevel = logging.WARNING):
        '''
            Specify the log format used in the webserver logs
            The webserver will catch stdout so we redirect eveything to sys.stdout
        '''
        log = logging.getLogger()
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('[%(asctime)s] %(module)s:%(lineno)d %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        log.setLevel(loglevel)
        log.addHandler(handler)
        return log


loglevel = logging.WARNING
try:
    debug = os.getenv('DEBUG',logging.WARNING)
    loglevel=int(debug)
except:
    print('Invalid LogLevel in DEBUG Environment Variable! "{}"'.format(debug) )
    loglevel = logging.WARNING

LOGGER = SAFRS.init_logging(loglevel)

#
# Following objects will be exported by safrs
#
# We put them at the bottom to avoid cicular dependencies
#
from .db import SAFRSBase, jsonapi_rpc
from .jsonapi import SAFRSJSONEncoder, Api, paginate
from .jsonapi import jsonapi_format_response, SAFRSFormattedResponse
from .errors import ValidationError, GenericError
from .api_methods import search, startswith



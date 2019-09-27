from os.path import join
from flask import Blueprint
from flask_restplus import Api
from src.apis import errors as api_errors
from src import config

REPORTS_FOLDER = join(config.ROOT_PATH, 'src', 'static', 'apis', 'reports')
TEMPLATES_FOLDER = join(config.ROOT_PATH, 'src', 'templates', 'apis', 'reports')

api_v1 = Blueprint('apis', __name__,
                   static_folder=REPORTS_FOLDER,
                   template_folder=TEMPLATES_FOLDER)
api = Api(api_v1,
          title="Authorisation Server Api",
          version="0.1.0",
          description="An API to generate reports and return them asd PDF or XML")


@api.errorhandler
def default_error_handler(error):
    error = api_errors.Server500Error(message='Internal Server Error')
    return error.to_response()


@api.errorhandler(api_errors.BadRequest400Error)
@api.errorhandler(api_errors.NotFound404Error)
@api.errorhandler(api_errors.Conflict409Error)
@api.errorhandler(api_errors.Server500Error)
def handle_error(error):
    return error.to_response()


# Add reports namespace
from src.apis.namespaces import reports
api.add_namespace(reports.api, '/reports')

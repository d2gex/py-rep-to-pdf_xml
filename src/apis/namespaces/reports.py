import json

from os.path import join
from flask import request
from flask_restplus import Resource, fields
from src import config
from src.apis import utils as api_utils, errors as api_errors
from src.apis.namespace import NameSpace
from src.engine import generate_reports

api = NameSpace('reports', description="Resource for clients to generate and return reports in either pdf or xml format")

report_generation_dto = api.model('Report Generation Data', {
    'report_id': fields.String(max_length=10, required=True, description="Number representing a report's unique_id"),
})

report_location_dto = api.model('Report Location Data', {
    'xml_url': fields.String(max_length=300, required=True, description="Absolute url where to find the xml report"),
    'pdf_url': fields.String(max_length=300, required=True, description="Absolute url where to find the pdf report"),
})

REPORTS_FOLDER = join(config.ROOT_PATH, 'src', 'static', 'apis', 'reports')
TEMPLATES_FOLDER = join(config.ROOT_PATH, 'src', 'templates', 'apis', 'reports')
DEFAULT_TEMPLATE_FILE = 'default.html'


@api.route('/')
@api.response_error(api_errors.Server500Error(message=api_utils.RESPONSE_500))
class ReportGenerator(Resource):

    @api.expect(report_generation_dto)
    @api.response_error(api_errors.BadRequest400Error(message=api_utils.RESPONSE_400))
    @api.response_error(api_errors.NotFound404Error(message=api_utils.RESPONSE_404))
    @api.response_error(api_errors.Conflict409Error(message=api_utils.RESPONSE_409))
    @api.response(201, json.dumps(api_utils.RESPONSE_201), body=False)
    def post(self):

        if not isinstance(api.payload, dict):
            raise api_errors.BadRequest400Error(
                message='Incorrect type of object received. Instead a json object is expected',
                envelop=api_utils.RESPONSE_400)

        # Do we have all expected fields?
        expected_fields = report_generation_dto.keys()
        for key in expected_fields:
            if key not in api.payload:
                raise api_errors.BadRequest400Error(message=f"Required key '{key}' not found",
                                                    envelop=api_utils.RESPONSE_400)

        # generate_reports(report_id, reports_folder, temps_folder, temp_file, data):
        ret = generate_reports(report_id=api.payload['report_id'],
                               reports_folder=REPORTS_FOLDER,
                               temps_folder=TEMPLATES_FOLDER,
                               temp_file=DEFAULT_TEMPLATE_FILE)

        # Has the report been found?
        if ret['code'] == 404:
            raise api_errors.NotFound404Error(message=ret['msg'],
                                              envelop=api_utils.RESPONSE_404)

        # Otherwise generate - if needed - and return the url to where the reports are
        response = dict(api_utils.RESPONSE_201)
        path_parts = ret['filename'].split('/')
        response['xml_url'] = f"{request.url}xml/{path_parts[-1]}.xml"
        response['pdf_url'] = f"{request.url}pdf/{path_parts[-1]}.pdf"
        response['report_id'] = api.payload['report_id']
        return response, 201


@api.route('/xml/<int:report_id>')
@api.response_error(api_errors.Server500Error(message=api_utils.RESPONSE_500))
class XMLReportProvider(Resource):

    @api.marshal_with(report_location_dto, description='An object such the structure below will be returned')
    @api.response_error(api_errors.NotFound404Error(message=api_utils.RESPONSE_404))
    def get(self, report_id):
        pass


@api.route('/pdf/<int:report_id>')
@api.response_error(api_errors.Server500Error(message=api_utils.RESPONSE_500))
class PDFReportProvider(Resource):

    @api.marshal_with(report_location_dto, description='An object such the structure below will be returned')
    @api.response_error(api_errors.NotFound404Error(message=api_utils.RESPONSE_404))
    def get(self, report_id):
        pass
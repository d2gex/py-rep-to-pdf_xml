import json

from flask_restplus import Resource, fields
from src.apis.namespace import NameSpace
from src.apis import utils as api_utils, errors as api_errors

api = NameSpace('reports', description="Resource for clients to generate and return reports in either pdf or xml format")

report_generation_dto = api.model('Report Generation Data', {
    'id': fields.String(max_length=10, required=True, description="Number representing a report's unique_id"),
})

report_location_dto = api.model('Report Location Data', {
    'xml_url': fields.String(max_length=300, required=True, description="Absolute url where to find the xml report"),
    'pdf_url': fields.String(max_length=300, required=True, description="Absolute url where to find the pdf report"),
})


@api.route('/')
@api.response_error(api_errors.Server500Error(message=api_utils.RESPONSE_500))
class ReportGenerator(Resource):

    @api.expect(report_generation_dto)
    @api.response_error(api_errors.BadRequest400Error(message=api_utils.RESPONSE_400))
    @api.response_error(api_errors.Conflict409Error(message=api_utils.RESPONSE_409))
    @api.response(201, json.dumps(api_utils.RESPONSE_201), body=False)
    def post(self):
        pass


@api.route('/xml/<int:report_id>')
@api.response_error(api_errors.Server500Error(message=api_utils.RESPONSE_500))
class XMLReportProvider(Resource):

    @api.marshal_with(report_location_dto, description='An object such the structure below will be returned')
    @api.response_error(api_errors.NotFound404Error(message=api_utils.RESPONSE_404))
    def get(self, report_id):
        pass


@api.route('/pdf/<int:report_id>')
@api.response_error(api_errors.Server500Error(message=api_utils.RESPONSE_500))
class XMLReportProvider(Resource):

    @api.marshal_with(report_location_dto, description='An object such the structure below will be returned')
    @api.response_error(api_errors.NotFound404Error(message=api_utils.RESPONSE_404))
    def get(self, report_id):
        pass
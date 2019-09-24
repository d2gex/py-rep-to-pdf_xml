import json

from unittest.mock import patch
from tests import utils as test_utils
RESOURCE_URI = '/api/reports/'


def test_post_errors(reports_app):
    '''Test than we posting to /reports:

    1) If data provided isn't the expected data structure => throw 400
    2) if data provided misses any expected key => 400
    3) if the report_id is not found => 404

    '''

    # (1)
    response = reports_app.post(RESOURCE_URI, data=json.dumps([]), content_type='application/json')
    assert response.status_code == 400
    ret_data = response.get_json()
    assert 400 == ret_data['error']['code']
    assert all(keyword in ret_data['error']['message'] for keyword in ('Invalid receive', 'Incorrect type'))

    # (2)
    response = reports_app.post(RESOURCE_URI,
                                data=json.dumps({'key_out_of_scope': 'something'}),
                                content_type='application/json')
    assert response.status_code == 400
    ret_data = response.get_json()
    assert 400 == ret_data['error']['code']
    assert all(keyword in ret_data['error']['message'] for keyword in ('Invalid receive', 'Required key'))

    # (3)
    response = reports_app.post(RESOURCE_URI,
                                data=json.dumps({'report_id': -1}),
                                content_type='application/json')
    ret_data = response.get_json()
    assert 404 == ret_data['error']['code']
    assert all(keyword in ret_data['error']['message'] for keyword in ('object has not been found', 'report'))


def test_post_generate_report_from_scratch(reports_app):
    '''Test than we posting to /reports and no reports exist, such reports are generated and url
    to reach tem is returned
    '''

    db_report = test_utils.get_db_report_for_test()
    response = reports_app.post(RESOURCE_URI,
                                data=json.dumps({'report_id': db_report.id}),
                                content_type='application/json')
    ret_data = response.get_json()
    assert response.status_code == 201
    assert all(key in ('xml_url', 'pdf_url', 'report_id') and value for key, value in ret_data.items())

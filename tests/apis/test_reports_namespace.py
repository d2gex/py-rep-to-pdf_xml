import pytest
import json
import uuid

from tests import utils as test_utils
from src.apis.handler import api_v1

TEMP_REPORTS_FOLDER = str(uuid.uuid4()).replace("-", "")


@pytest.fixture(scope='module', autouse=True)
def change_static_folder_path(tmpdir_factory):
    '''Generator required to monkey patch the path of the REPORTS_FOLDER so that reports generated as part of this
    test do not mess up the real production code location. Once all tests have been run, the original production
    location is re-established
    '''
    original_path = api_v1.static_folder
    new_temp_path = tmpdir_factory.mktemp(TEMP_REPORTS_FOLDER)
    try:
        api_v1.static_folder = new_temp_path
        yield
    finally:
        api_v1.static_folder = original_path

# create_app needs to be imported after the above scoped module generator runs and change at runtime the path
# where to drop the report files. No pretty but necessary
from src.app import create_app
from tests.config_test import TestConfig


@pytest.fixture
def reports_app():
    app = create_app(config_class=TestConfig)
    return app.test_client(use_cookies=True)


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
    to reach them is returned
    '''

    db_report = test_utils.get_db_report_for_test()
    response = reports_app.post(RESOURCE_URI,
                                data=json.dumps({'report_id': db_report.id}),
                                content_type='application/json')
    ret_data = response.get_json()
    assert response.status_code == 201
    assert all(key in ('xml_url', 'pdf_url', 'report_id') and value for key, value in ret_data.items())

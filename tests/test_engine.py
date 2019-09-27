import json

from os.path import join
from src import models
from src.app import db
from src import engine
from tests import utils as test_utils
from unittest.mock import patch


def test_generate_reports_not_found():
    '''Issue a report not found error when the report is not found in the database
    '''

    report_id = -1
    args = [None for _ in range(4)]
    ret = engine.generate_reports(report_id, *args)
    assert ret['code'] == 404
    assert ret['msg'] == f"report '{report_id}' not found"
    assert not ret['filename']


def test_generate_reports_processing_status():
    '''Issue a 200 code and a corresponding message when the report is being processed
    '''

    db_report = test_utils.get_db_report_for_test()
    db_report = test_utils.toggle_processing_flag(db_report)
    assert db_report.processing == 1

    args = [None for _ in range(4)]
    ret = engine.generate_reports(db_report.id, *args)
    assert ret['code'] == 200
    assert ret['msg'] == f"Report '{db_report.id}' is being generated"
    assert not ret['filename']


def test_generate_reports_from_scratch(tmp_path):
    '''Ensure that if no reports have been generated yet, then they are generated and the filename returned.
    The content of the report is provided
    '''
    db_report = test_utils.get_db_report_for_test()
    reports_folder = tmp_path / "reports"
    reports_folder.mkdir()

    ret = engine.generate_reports(db_report.id,
                                  reports_folder=reports_folder,
                                  temps_folder=test_utils.TEMPLATE_FOLDER,
                                  temp_file=test_utils.TEMPLATE_FILE,
                                  data=test_utils.data)
    assert ret['code'] == 301
    assert ret['msg'] == f"Report {db_report.id} has just been generated"
    assert ret['filename']

    db_report = db.session.query(models.Reports).filter_by(id=db_report.id).one()
    xml_path, xml_ext = db_report.xml_path.split('.')
    pdf_path, pdf_ext = db_report.pdf_path.split('.')
    assert xml_path == pdf_path
    assert xml_ext == 'xml'
    assert pdf_ext == 'pdf'


def test_check_processing_flag_is_toggle_when_generating_reports(tmp_path):
    '''Ensure that when generating a report from the scratch the 'processing' flag on the database is set to 1
    prior to creating and saving the report and then after.
    '''

    db_report = test_utils.get_db_report_for_test()
    reports_folder = tmp_path / "reports"
    reports_folder.mkdir()

    with patch.object(engine.db, 'session') as mock_db_session:

        db_report_mock = mock_db_session.query.return_value.filter_by.return_value.one.return_value
        db_report_mock.processing = 0
        db_report_mock.pdf_path = None
        engine.generate_reports(db_report.id,
                                reports_folder=reports_folder,
                                temps_folder=test_utils.TEMPLATE_FOLDER,
                                temp_file=test_utils.TEMPLATE_FILE,
                                data=test_utils.data)
    mock_update = mock_db_session.query.return_value.filter_by.return_value.update
    assert mock_update.call_count == 2
    first_call = mock_update.call_args_list[0][0][0]
    assert 'processing' in first_call and first_call['processing'] == 1
    second_call = mock_update.call_args_list[1][0][0]
    assert 'processing' in second_call and second_call['processing'] == 0


def test_generate_reports_from_existing():
    '''Ensure that if the report has been generated, then the filename is returned. The content
    of the report is provided.
    '''

    db_report = test_utils.get_db_report_for_test()
    filename = 'report_filename'
    db.session. \
        query(models.Reports). \
        filter_by(id=db_report.id). \
        update({'xml_path': f'{filename}.xml', 'pdf_path': f'{filename}.pdf'})
    db_report = db.session.query(models.Reports).filter_by(id=db_report.id).one()
    args = [None for _ in range(4)]

    ret = engine.generate_reports(db_report.id, *args)
    assert ret['code'] == 301
    assert ret['msg'] == f"Report {db_report.id} is was already available"
    assert ret['filename']

    db_report = db.session.query(models.Reports).filter_by(id=db_report.id).one()
    xml_path, xml_ext = db_report.xml_path.split('.')
    pdf_path, pdf_ext = db_report.pdf_path.split('.')
    assert xml_path == pdf_path
    assert xml_path == filename
    assert xml_ext == 'xml'
    assert pdf_ext == 'pdf'


def test_generate_report_from_scratch_no_data_provided(tmp_path):
    '''Unless the other tests above this test will ensure that the content of the report is actually
    picked from the database instead of provided.
    '''
    db_report = test_utils.get_db_report_for_test()
    reports_folder = tmp_path / "reports"
    reports_folder.mkdir()

    db.session. \
        query(models.Reports). \
        filter_by(id=db_report.id). \
        update({'content': json.dumps(test_utils.data)})

    ret = engine.generate_reports(db_report.id,
                                  reports_folder=reports_folder,
                                  temps_folder=test_utils.TEMPLATE_FOLDER,
                                  temp_file=test_utils.TEMPLATE_FILE)

    assert ret['code'] == 301
    assert ret['msg'] == f"Report {db_report.id} has just been generated"
    assert ret['filename']
    with open(join(reports_folder, f"{ret['filename']}.xml")) as fh:
        data = fh.read()

    # Organisation should be the same as the one persisted in the database which is test_utils.data
    assert test_utils.data['organisation'] in data

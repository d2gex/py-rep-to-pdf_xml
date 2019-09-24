
from src import models
from src.app import db
from src.engine import generate_reports
from tests import utils as test_utils


def get_db_report_for_test():
    test_utils.fill_db_with_test_data()
    db_data = db.session.query(models.Reports).all()
    for report in db_data:
        if 'Dunder Mifflin' in report.content:
            break
    return report


def toggle_processing_flag(report):

    report.processing = 1 if not report.processing else 0
    db.session.add(report)
    db.session.commit()
    db_report = db.session.query(models.Reports).filter_by(id=report.id).one()
    return db_report


def test_generate_reports_not_found():
    '''Issue a report not found error when the report is not found in the database
    '''

    report_id = -1
    args = [None for _ in range(4)]
    ret = generate_reports(report_id, *args)
    assert ret['code'] == 404
    assert ret['msg'] == f"report '{report_id}' not found"
    assert not ret['filename']


def test_generate_reports_processing_status():
    '''Issue a 200 code and a corresponding message when the report is being processed
    '''

    db_report = get_db_report_for_test()
    db_report = toggle_processing_flag(db_report)
    assert db_report.processing == 1

    args = [None for _ in range(4)]
    ret = generate_reports(db_report.id, *args)
    assert ret['code'] == 200
    assert ret['msg'] == f"Report '{db_report.id}' is being generated"
    assert not ret['filename']


def test_generate_reports_from_scratch(tmp_path):
    '''Ensure that if no reports have been generated yet, then they are generated and the filename returned
    '''
    db_report = get_db_report_for_test()
    reports_folder = tmp_path / "reports"
    reports_folder.mkdir()

    ret = generate_reports(db_report.id,
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


def test_generate_reports_from_existing():
    '''Ensure that if the report has been generated, then the filename is returned
    '''

    db_report = get_db_report_for_test()
    filename = 'report_filename'
    db.session. \
        query(models.Reports). \
        filter_by(id=db_report.id). \
        update({'xml_path': f'{filename}.xml', 'pdf_path': f'{filename}.pdf'})
    db_report = db.session.query(models.Reports).filter_by(id=db_report.id).one()
    args = [None for _ in range(4)]

    ret = generate_reports(db_report.id, *args)
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

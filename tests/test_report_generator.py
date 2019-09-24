import pytest

from os.path import join, exists
from src.report_generator import ReportGenerator
from tests import utils as test_utils

TEMPLATE_FOLDER = join(test_utils.TEST, 'stubs')
TEMPLATE_FILE = 'temp_1.html'
data = {
        'organisation': 'Lorem Ipsum Ltd',
        'reported_at': "2015-04-21",
        'inventory': [
            {
                'name': 'A',
                'price': 5.0
            },
            {
                'name': 'B',
                'price': 7.0
            }
        ]
    }


@pytest.fixture
def rep_gen(tmp_path):
    temp_reports = tmp_path / 'reports'
    temp_reports.mkdir()
    return ReportGenerator(reports_folder=temp_reports, temps_folder=TEMPLATE_FOLDER, data=data)


def test_to_pdf(rep_gen, tmp_path):
    pdf_file = f"{rep_gen.filename}.pdf"
    assert exists(tmp_path / 'reports')
    assert not exists(pdf_file)
    rep_gen.to_pdf(TEMPLATE_FILE)
    assert exists(pdf_file)


def test_to_xml(rep_gen, tmp_path):
    xml_file = f"{rep_gen.filename}.xml"
    assert exists(tmp_path / 'reports')
    assert not exists(xml_file)
    rep_gen.to_xml()
    assert exists(xml_file)


def test_run(rep_gen):
    '''Ensure that both the PDF and XML reports are generated and saved to the filesystem
    '''

    # Ensure reports are generated and stored
    pdf_file = f"{rep_gen.filename}.pdf"
    xml_file = f"{rep_gen.filename}.xml"
    assert not exists(pdf_file)
    assert not exists(xml_file)
    rep_gen.run(TEMPLATE_FILE)
    assert exists(pdf_file)
    assert exists(xml_file)

    # ensure filename property returns the filename without extension
    assert rep_gen.filename
    assert '.' not in rep_gen.filename

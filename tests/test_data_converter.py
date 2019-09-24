import pytest
import json

from os.path import join
from src.data_converter import HTMLToPDF, JSONToXML
from tests.utils import TEST, data


@pytest.fixture(scope='module')
def html_to_pdf():
    return HTMLToPDF(join(TEST, 'stubs'))


def test_template_renders_ok(html_to_pdf):
    '''Ensure that Jinja2 renders template properly with its placeholders
    '''

    rendered_temp = html_to_pdf.render('temp_1.html', data)
    assert data['organisation'] in rendered_temp
    assert data['reported_at'] in rendered_temp
    assert all(str(value) in rendered_temp for x in data['inventory'] for key, value in x.items())


def test_html_to_pdf(html_to_pdf):
    '''Ensure a bytes object is returned as part of the html to pdf conversion
    '''

    pdf = html_to_pdf.convert('temp_1.html', data)
    assert isinstance(pdf, bytes)


def test_json_to_xml():
    '''Ensure a JSON string is converted to well-formed xml
    '''

    # Test valid JSON
    jxml = JSONToXML()
    xml = jxml.convert(json.dumps(data))
    assert data['organisation'] in xml
    assert data['reported_at'] in xml
    assert all(str(value) in xml for x in data['inventory'] for key, value in x.items())

    # Test invalid json
    with pytest.raises(json.decoder.JSONDecodeError):
        jxml.convert("This is an invalid JSON string")

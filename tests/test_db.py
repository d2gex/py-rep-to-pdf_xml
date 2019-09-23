import uuid

from src import models
from src.app import db
from tests import utils as test_utils


@test_utils.reset_database()
def test_db():
    report = models.Reports()
    f_name = str(uuid.uuid4()).replace('-', '')
    report.pdf_path = f"{f_name}.pdf"
    report.xml_path = f"{f_name}.xml"
    db.session.add(report)
    db.session.commit()
    db_data = db.session.query(models.Reports).one()
    assert db_data.pdf_path == report.pdf_path
    assert db_data.xml_path == report.xml_path

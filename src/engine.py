import json

from os.path import join
from sqlalchemy.orm.exc import NoResultFound
from src import models
from src.report_generator import ReportGenerator
from src.app import db


def generate_reports(report_id, reports_folder, temps_folder, temp_file, data=None):
    '''Given a report ID and format it returns a report
    '''

    code = 200
    msg = None
    filename = None

    # Does the report exist?
    try:
        db_report = db.session.query(models.Reports).filter_by(id=report_id).one()
    except NoResultFound:
        code = 404
        msg = f"report '{report_id}' not found"
    else:
        # ... Is the report being processed?
        if db_report.processing:
            msg = f"Report '{report_id}' is being generated"
        else:
            code = 301
            # ... Do we need to generate a new report?
            if not db_report.pdf_path:
                # Set 'processing' flag to 1 to avoid others to regenerate the reports
                db.session. \
                    query(models.Reports). \
                    filter_by(id=report_id). \
                    update({'processing': 1})
                rep_gen = ReportGenerator(reports_folder=reports_folder,
                                          temps_folder=temps_folder,
                                          data=json.loads(db_report.content) if not data else data)
                rep_gen.filename = join(reports_folder, str(report_id))
                rep_gen.run(temp_file)
                filename = rep_gen.filename
                # Update paths and toggle 'processing' flag
                db.session.\
                    query(models.Reports).\
                    filter_by(id=report_id).\
                    update({'xml_path': f'{filename}.xml', 'pdf_path': f'{filename}.pdf', 'processing': 0})
                msg = f"Report {report_id} has just been generated"
            # ... or does the report exist?
            else:
                filename, *rest = db_report.pdf_path.split('.')
                msg = f"Report {report_id} is was already available"

    return {
        'code': code,
        'msg': msg,
        'filename': filename
    }

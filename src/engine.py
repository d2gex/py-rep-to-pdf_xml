from sqlalchemy.orm.exc import NoResultFound
from src import models
from src.report_generator import ReportGenerator
from src.app import db


def generate_reports(report_id, reports_folder, temps_folder, temp_file, data):
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
                rep_gen = ReportGenerator(reports_folder=reports_folder, temps_folder=temps_folder, data=data)
                rep_gen.run(temp_file)
                filename = rep_gen.filename
                db.session.\
                    query(models.Reports).\
                    filter_by(id=report_id).\
                    update({'xml_path': f'{filename}.xml', 'pdf_path':f'{filename}.pdf'})
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

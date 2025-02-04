import functools

from os.path import join
from pathlib import Path
from sqlalchemy import Table
from src import models
from src.app import db

path = Path(__file__).resolve()
ROOT = path.parents[1]
TEST = join(ROOT, 'tests')

TEMPLATE_FOLDER = join(TEST, 'stubs')
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

table_names = [models.Reports]


def queries(tables):
    '''Generator that will create the required queries to reset a list of tables passed as parameters
    '''
    for obj in tables:
        yield db.session.execute(obj.delete()) if isinstance(obj, Table) else db.session.query(obj).delete()


def reset_database(tear='up', tables=None):
    ''' Reset the database before, after or before and after the method being decorated is executed.
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _tables = table_names if not tables else tables
            if tear in ('up', 'up_down'):
                list(queries(_tables))
                db.session.commit()
            ret = func(*args, **kwargs)
            if tear in ('down', 'up_down'):
                list(queries(_tables))
                db.session.commit()
            return ret
        return wrapper
    return decorator


def fill_db_with_test_data():
    '''It will fill up the database with data useful for testing
    '''
    db.session.add(models.Reports(
        content='{"organization":"Dunder Mifflin","reported_at":"2015-04-21","created_at":"2015-04-22",'
                '"inventory":[{"name":"paper","price":"2.00"},{"name":"stapler","price":"5.00"}]}'
    ))
    db.session.add(models.Reports(
        content='{"organization":"MOM Corp.","reported_at":"3015-08-24","created_at":"3015-08-23",'
                '"inventory":[{"name":"bending unit","price":"2000.00"},{"name":"stapling unit","price":"50.00"}]}'
    ))
    db.session.add(models.Reports(
        content='{"organization":"Flowers Inc.","reported_at":"2017-11-19","created_at":"2017-11-23",'
                '"inventory":[{"name":"Flower pot","price":"2.00"},{"name":"Roses, 24","price":"50.00"}]}'
    ))
    db.session.add(models.Reports(
        content='{invalid_json'
    ))
    db.session.commit()


def get_db_report_for_test():
    fill_db_with_test_data()
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

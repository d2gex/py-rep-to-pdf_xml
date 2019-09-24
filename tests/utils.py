import functools

from os.path import join
from pathlib import Path
from sqlalchemy import Table
from src import models
from src.app import db

path = Path(__file__).resolve()
ROOT = path.parents[1]
TEST = join(ROOT, 'tests')

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

from src.app import db
from unittest.mock import patch
from tests import utils as test_utils
from src import models


def test_queries():
    '''Test queries generator generates the right delete queries depending on the type of object of a given list
    '''

    tables = [models.Reports()]
    with patch.object(test_utils.db.session, 'query') as qy_model:
        list(test_utils.queries(tables))
    assert qy_model.call_count == len(tables)


def test_reset_database():
    '''Test that reset_database works as follows:

    1) When tear='up' => the generator is only consumed once and before foo executes.
    2) When tear='down' => the generator is only consumed once and after bar executes.
    2) When tear='up_down' => the generator is consumed twice, before and after foo_bar.

    '''

    tables = [models.Reports()]
    with patch.object(test_utils.db.session, 'query') as qy_model:
        with patch.object(test_utils.db.session, 'commit'):

            # (1)
            @test_utils.reset_database(tear='up', tables=tables)
            def foo():
                # By the time this lines run, the database should have been reset so ex_table and qy_model should
                # have already a value
                assert qy_model.call_count == len(tables)

            foo()
            assert qy_model.call_count == len(tables)

            qy_model.reset_mock()

            # (2)
            @test_utils.reset_database(tear='down', tables=tables)
            def bar():
                # By the time this lines run, the database should have been reset so ex_table and qy_model should
                # have already a value
                assert qy_model.call_count == 0

            bar()
            assert qy_model.call_count == len(tables)

            qy_model.reset_mock()

            # (3)
            @test_utils.reset_database(tear='up_down', tables=tables)
            def foo_bar():
                # By the time this lines run, the database should have been reset so ex_table and qy_model should
                # have already a value
                assert qy_model.call_count == len(tables)

            foo_bar()
            assert qy_model.call_count == 2 * len(tables)


def test_fill_db_with_test_data():
    assert not db.session.query(models.Reports).all()
    test_utils.fill_db_with_test_data()
    assert len(db.session.query(models.Reports).all()) == 4

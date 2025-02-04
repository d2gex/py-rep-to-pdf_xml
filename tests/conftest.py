import pytest

from src import config
from src.app import create_app
from tests import utils as test_utils
from tests.config_test import TestConfig


@pytest.fixture(scope='session', autouse=True)
def app_context():
    app = create_app(config_class=TestConfig)
    with app.app_context():
        yield


@pytest.fixture(autouse=True)
@test_utils.reset_database(tear='up')
def reset_database():
    '''Reset the database before any test is run
    '''
    yield


@pytest.fixture
def reports_app():
    app = create_app(config_class=TestConfig)
    return app.test_client(use_cookies=True)

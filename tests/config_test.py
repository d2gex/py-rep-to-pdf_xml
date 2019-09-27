from src import config

class TestConfig(config.Config):

    # Needed for form's unit test validation
    WTF_CSRF_ENABLED = False
import os

from pathlib import Path
from dotenv import load_dotenv
from os.path import join

path = Path(__file__).resolve()
ROOT_PATH = str(path.parents[1])
dot_env = load_dotenv(join(ROOT_PATH, '.env'))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f"postgresql://" \
                              f"{os.getenv('DB_USER')}:" \
                              f"{os.getenv('DB_PASSWORD')}@" \
                              f"{os.getenv('DB_HOST')}/" \
                              f"{os.getenv('DB')}"
    RESTPLUS_MASK_SWAGGER = False  # Do not show X-FIELDS in swagger

import logging
import os
import random
import shutil
from configparser import ConfigParser

import faker
import pytest

import dropboxer.models


@pytest.fixture(scope='session')
def here():
    return os.path.dirname(os.path.abspath(__file__))


@pytest.fixture()
def sandbox(here):
    sandbox_path = os.path.join(here, 'sandbox')
    os.makedirs(sandbox_path)
    yield sandbox_path
    shutil.rmtree(sandbox_path)


@pytest.fixture(scope='session')
def config(here):
    config = ConfigParser()
    config.read(os.path.join(here, 'config.ini'))
    return config


@pytest.fixture(scope='session')
def fake():
    return faker.Faker()


@pytest.fixture(autouse=True, scope='session')
@pytest.mark.fixture(autouse=True, scope='session')
def setup_logging(config):
    if config.has_section('logging'):
        logging.config.dictConfig(config['logging'])
    else:
        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(levelname)-5.5s] [%(name)s] %(smg)s')


@pytest.fixture(autouse=True, scope='session')
def database(config):
    dropboxer.models.configure(config['main'])
    dropboxer.models.Base.metadata.create_all()

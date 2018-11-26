import logging
import os
import shutil
from configparser import ConfigParser

import pytest

import dropboxer.models


here = os.path.dirname(os.path.abspath(__file__))
@pytest.fixture(scope='session')
def config():
    config = ConfigParser()
    config.read(os.path.join(here, 'config.ini'))
    return config


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
    # configure database connection
    dropboxer.models.configure(config['main'])
    dropboxer.models.Base.metadata.create_all()

    # create transfer directories
    source_directory = os.path.join(here, 'source')
    sink_directories = [
        os.path.join(here, 'sink_1'),
        os.path.join(here, 'sink_2')]
    directories = [source_directory] + sink_directories
    for directory in directories:
        if os.path.isdir(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)

    # populate database
    with dropboxer.models.transaction() as session:
        # add sinks
        for i, sink_directory in enumerate(sink_directories):
            sink = dropboxer.models.TransferSink(
                name=f'sink_{i}',
                path=sink_directory)
            session.add(sink)

    yield

    # cleanup
    for directory in directories:
        shutil.rmtree(directory)

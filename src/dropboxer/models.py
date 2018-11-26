import logging

from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    engine_from_config,
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    relationship,
    sessionmaker,
    )


Base = declarative_base()
Session = sessionmaker()


class TransferRule(Base):
    __tablename__ = 'rules'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    source_path = Column(String)
    date_added = Column(DateTime, default=datetime.now)


class TransferSink(Base):
    __tablename__ = 'sinks'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)


def configure(config):
    engine = engine_from_config(config, 'database.')
    Base.metadata.bind = engine
    Session.configure(bind=engine)


@contextmanager
def transaction(commit=False):
    session = Session()
    session_id = id(session)

    logger = logging.getLogger(f'{__name__}.transaction.{session_id}')
    log_extra = {'session': {'id': session_id}}
    logger = logging.LoggerAdapter(logger, log_extra)
    logger.debug('create', extra=log_extra)

    try:
        yield session
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.debug('rollback')
        session.rollback()
        raise
    else:
        if commit:
            logger.debug('commit')
            session.commit()
        else:
            logger.debug('rollback')
            session.rollback()
    finally:
        logger.debug('close')
        session.close()

import logging
import os
import time

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

from .utils import (
    GetLoggerMixin,
    )


Base = declarative_base()
Session = sessionmaker()


class TransferRule(Base, GetLoggerMixin):
    __loggername__ = f'{__name__}.TransferRule'

    __tablename__ = 'rules'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    date_added = Column(DateTime, default=datetime.now)

    paths = relationship('TransferRulePath', back_populates='rule')

    @classmethod
    def create(cls, session, name, paths=[]):
        transfer_rule = cls(name=name)
        session.add(transfer_rule)
        session.flush()
        return transfer_rule

    def run(self, session):
        logger = cls._logger('run')
        logger.debug(self.name)

    @classmethod
    def run_all(session):
        logger = cls._logger('run_all')
        logger.debug('start')

        count = 0
        start = time.time()
        for rule in session.query(cls).all():
            rule.run(session)
            count += 1

        time_elapsed = time.time() - start
        logger.debug('ran {count} rules', extra={
            'time_elapsed': time_elapsed})

        return count


class TransferRulePath(Base, GetLoggerMixin):
    __loggername__ = f'{__name__}.TransferRulePath'

    __tablename__ = 'rule_paths'
    id = Column(Integer, primary_key=True)
    rule_id = Column(Integer, ForeignKey('rules.id'))
    source_id = Column(Integer, ForeignKey('paths.id'))
    sink_id = Column(Integer, ForeignKey('paths.id'))

    rule = relationship('TransferRule', foreign_keys=[rule_id])
    source = relationship('TransferPath', foreign_keys=[source_id])
    sink = relationship('TransferPath', foreign_keys=[sink_id])

    @classmethod
    def create(cls, session, source, sink):
        logger = cls._logger('create')
        logger.debug(f'{source.path} -> {sink.path}')

        exists = session.query(cls) \
                .filter(cls.source_id == source.id) \
                .filter(cls.sink_id == sink.id) \
                .count()
        if exists:
            logger.warning('rule path ({source.path} -> {sink.path}) already exists')
            return False

        rule_path = cls(
            source_id=source.id,
            sink_id=sink.id)
        session.add(rule_path)
        session.flush()

        return rule_path


class TransferPath(Base, GetLoggerMixin):
    __loggername__ = f'{__name__}.TransferPath'

    __tablename__ = 'paths'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String, unique=True)
    type = Column(String)
    date_added = Column(DateTime, default=datetime.now)

    @classmethod
    def create(cls, session, name, path, type):
        logger = cls._logger('create')
        logger.debug(f'{name}: {path} ({type})')

        if os.path.isdir(path):
            logger.warning('path alredy exists: {path}')
            return False
        os.makedirs(path)

        transfer_path = cls(name=name, path=path, type=type)
        session.add(transfer_path)
        session.flush()
        return transfer_path

    @classmethod
    def delete(cls, session, id_):
        logger = cls._logger('delete')
        logger.debug(id_)

        transfer_path = session.query(cls).get(id_)
        if not transfer_path:
            logger.warning('path with id {id_} does not exist')
            return False

        session.delete(transfer_path)
        return True


def configure(config):
    engine = engine_from_config(config, 'database.')
    Base.metadata.bind = engine
    Session.configure(bind=engine)


@contextmanager
def transaction(commit=True):
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

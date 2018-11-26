import os
import random

import pytest

import dropboxer
from dropboxer.models import (
    TransferPath,
    TransferRule,
    TransferRulePath,
    transaction,
    )


@pytest.mark.parametrize('type', ['source', 'sink'])
@pytest.mark.path
@pytest.mark.create
def test_create_path(sandbox, fake, type):
    name = fake.word()
    path = os.path.join(sandbox, name)
    with transaction() as session:
        transfer_path = TransferPath.create(
            session,
            name=name,
            path=path,
            type=type)
        id = transfer_path.id

    # fetch it by its id
    with transaction() as session:
        transfer_path = session.query(TransferPath).get(id)
        assert transfer_path.id == id
    # fetch it by its path
    with transaction() as session:
        transfer_path = session.query(TransferPath) \
                .filter(TransferPath.path == path) \
                .one()
        assert transfer_path.id == id


@pytest.mark.path
@pytest.mark.create
@pytest.mark.invalid
def test_create_path_that_already_exists(sandbox, fake):
    name = fake.word()
    path = os.path.join(sandbox, name)

    # create a path
    with transaction() as session:
        transfer_path = TransferPath.create(
            session,
            name=name,
            path=path,
            type='source')
    
    # try to create the same path
    with transaction() as session:
        invalid_transfer_path = TransferPath.create(
            session,
            name=name,
            path=path,
            type='source')
        assert invalid_transfer_path is False


@pytest.mark.path
@pytest.mark.delete
def test_delete_path(sandbox, fake):
    name = fake.word()
    path = os.path.join(sandbox, name)
    with transaction() as session:
        transfer_path = TransferPath.create(
            session,
            name=name,
            path=path,
            type='source')
        id_ = transfer_path.id

    with transaction() as session:
        assert TransferPath.delete(session, id_) is True

    with transaction() as session:
        assert session.query(TransferPath).get(id_) is None


@pytest.mark.path
@pytest.mark.delete
@pytest.mark.invalid
def test_delete_nonexistent_path():
    id_ = random.randint(1000, 2000)
    with transaction() as session:
        assert TransferPath.delete(session, id_) is False


@pytest.mark.rule_path
@pytest.mark.create
def test_create_rule_path(sandbox, fake):
    with transaction() as session:
        source_name = fake.word()
        source_path = os.path.join(sandbox, source_name)
        source = TransferPath.create(
            session,
            name=source_name,
            path=source_path,
            type='source')

        sink_name = fake.word()
        sink_path = os.path.join(sandbox, sink_name)
        sink = TransferPath.create(
            session,
            name=sink_name,
            path=sink_path,
            type='sink')

        rule_path = TransferRulePath.create(
            session,
            source,
            sink)
        rule_path_id = rule_path.id

    with transaction() as session:
        rule_path = session.query(TransferRulePath).get(rule_path_id)
        assert rule_path.source.path == source_path
        assert rule_path.sink.path == sink_path


@pytest.mark.rule_path
@pytest.mark.create
@pytest.mark.invalid
def test_create_rule_path_that_already_exists(sandbox, fake):
    with transaction() as session:
        source_name = fake.word()
        source_path = os.path.join(sandbox, source_name)
        source = TransferPath.create(
            session,
            name=source_name,
            path=source_path,
            type='source')

        sink_name = fake.word()
        sink_path = os.path.join(sandbox, sink_name)
        sink = TransferPath.create(
            session,
            name=sink_name,
            path=sink_path,
            type='sink')

        rule_path = TransferRulePath.create(session, source, sink)
        _rule_path = TransferRulePath.create(session, source, sink)
        assert _rule_path is False


@pytest.mark.rule
@pytest.mark.create
def test_create_rule(sandbox, fake):
    with transaction() as session:
        rule_name = fake.word()
        rule = TransferRule.create(session, name=rule_name)
        rule_id = rule.id

    with transaction() as session:
        rule = session.query(TransferRule).get(rule_id)
        assert rule.name == rule_name

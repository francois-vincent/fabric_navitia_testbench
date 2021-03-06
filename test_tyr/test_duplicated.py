# encoding: utf-8

import time

from ..test_common import skipifdev


instances_names = {'us-wa', 'fr-nw', 'fr-npdc', 'fr-ne-amiens', 'fr-idf', 'fr-cen'}


@skipifdev
def test_tyr_setup(duplicated):
    platform, fabric = duplicated
    assert platform.path_exists('/var/log/tyr')
    assert platform.path_exists('/srv/ed/data')
    assert platform.path_exists('/etc/tyr.d')
    for krak in instances_names:
        assert platform.path_exists('/srv/ed/{}'.format(krak))


@skipifdev
def test_create_remove_tyr_instance(duplicated):
    platform, fabric = duplicated
    fabric.get_object('instance.add_instance')('toto', 'passwd',
                       zmq_socket_port=30004, zmq_server=fabric.env.host1_ip)
    # postgres is really long to warm up !
    time.sleep(15)

    with fabric.set_call_tracker('component.db.create_instance_db') as data:
        value, exception, stdout, stderr = fabric.execute_forked('create_tyr_instance', 'toto')
    assert exception is None
    assert stderr == ''

    # create_instance_db should be called only once
    assert len(data()['create_instance_db']) == 2
    assert stdout.count('Really run create_instance_db') == 1
    # tyr and db instances are created on both machines
    assert stdout.count("Executing task 'create_tyr_instance'") == 2
    assert stdout.count("Executing task 'create_instance_db'") == 2
    assert platform.path_exists('/srv/ed/data/toto')
    assert platform.path_exists('/srv/ed/data/toto/backup')
    assert platform.path_exists('/srv/ed/toto')
    assert platform.path_exists('/var/log/tyr/toto.log')
    assert platform.path_exists('/etc/tyr.d/toto.ini')
    assert platform.path_exists('/srv/ed/toto/alembic.ini')
    assert platform.path_exists('/srv/ed/toto/settings.sh')

    time.sleep(2)
    with fabric.set_call_tracker('component.tyr.restart_tyr_worker',
                                 'component.tyr.restart_tyr_beat') as data:
        value, exception, stdout, stderr = fabric.execute_forked('remove_tyr_instance', 'toto', purge_logs=True)

    assert exception is None
    assert stderr == ''
    assert stdout.count("Executing task 'remove_tyr_instance'") == 2
    assert platform.path_exists('/etc/tyr.d/toto.ini', negate=True)
    assert platform.path_exists('/var/log/tyr/toto.log', negate=True)
    # restart_tyr_worker is called on both machines (good)
    assert len(data()['restart_tyr_worker']) == 2
    assert set((x[2] for x in data()['restart_tyr_worker'])) == set(fabric.env.roledefs['tyr'])
    # restart_tyr_beat is called twice on tyr_master (not so good)
    assert len(data()['restart_tyr_beat']) == 2
    assert set((x[2] for x in data()['restart_tyr_beat'])) == set(fabric.env.roledefs['tyr_master'])

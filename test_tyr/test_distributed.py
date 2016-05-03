# encoding: utf-8

from ..test_common import skipifdev


@skipifdev
def test_create_remove_tyr_instance(distributed, capsys):
    platform, fabric = distributed
    fabric.get_object('instance.add_instance')('toto', 'passwd',
                       zmq_socket_port=30004, zmq_server=fabric.env.host1_ip)
    fabric.execute('create_tyr_instance', 'toto')
    out, err = capsys.readouterr()
    assert out.count("Executing task 'create_tyr_instance'") == 2
    assert out.count("Executing task 'create_instance_db'") == 2
    assert out.count("Actually running create_instance_db") == 1
    assert platform.path_exists('/srv/ed/data/toto')
    assert platform.path_exists('/srv/ed/data/toto/backup')
    assert platform.path_exists('/srv/ed/toto')
    assert platform.path_exists('/var/log/tyr/toto.log')
    assert platform.path_exists('/etc/tyr.d/toto.ini')
    assert platform.path_exists('/srv/ed/toto/alembic.ini')
    assert platform.path_exists('/srv/ed/toto/settings.sh')
    fabric.execute('remove_tyr_instance', 'toto', purge_logs=True)
    out, err = capsys.readouterr()
    assert out.count("Executing task 'remove_tyr_instance'") == 2
    assert platform.path_exists('/etc/tyr.d/toto.ini', negate=True)
    assert platform.path_exists('/var/log/tyr/toto.log', negate=True)

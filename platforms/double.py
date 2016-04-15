# encoding: utf-8

from fabric.api import env
from fabfile.instance import add_instance
from common import env_common


def double(host1, host2):
    env_common(host1, host1, [host1, host2], host1)
    env.name = 'simple'

    env.postgresql_database_host = 'localhost'

    env.postgresql_database_host = 'localhost'
    env.use_zmq_socket_file = False
    env.use_syslog = False
    env.rabbitmq_host = 'localhost'

    # WARNING passwords should not contain special characters except star (*)
    add_instance("fr-nw", "passwd", zmq_socket_port=30006, is_free=True, zmq_server='localhost')
    add_instance("fr-ne-amiens", "passwd*", zmq_socket_port=30019, zmq_server=host2)
    add_instance("fr-idf", "passwd", zmq_socket_port=30002, is_free=True, zmq_server=host2)
    add_instance("fr-cen", "passwd", zmq_socket_port=30000, zmq_server=host2)
    add_instance("us-wa", "passwd", zmq_socket_port=30023, is_free=True, zmq_server='localhost')
    add_instance("fr-npdc", "passwd", zmq_socket_port=30018, zmq_server='localhost')

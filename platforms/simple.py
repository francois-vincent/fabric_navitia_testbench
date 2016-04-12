# encoding: utf-8

from fabric.api import env
from fabfile.instance import add_instance
from common import env_common


def simple(host):
    env_common(host, host, host, host)
    env.name = 'simple'

    env.postgresql_database_host = 'localhost'

    add_instance('default', 'default')

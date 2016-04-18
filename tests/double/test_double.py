# encoding: utf-8

import os.path
import time

from fabric import api

from ...docker import ROOTDIR, get_container_ip
from ...utils import extract_column

ROOTDIR = os.path.dirname(os.path.abspath(__file__))


def test_containers(platform):
    platform, fabric = platform

    # ---- tests
    # check platform instantiation in fabric
    assert api.env.name == 'double'
    assert api.env.roledefs['eng'] == ['root@' + get_container_ip('debian8_double_host1'),
                                       'root@' + get_container_ip('debian8light_double_host2')]
    # Check the images are there
    assert set(platform.get_real_images()) == {'debian8', 'debian8light'}
    # Check the containers are running
    assert set(platform.get_real_containers()) == {'debian8_double_host1', 'debian8light_double_host2'}
    # Check I can ssh to it
    assert platform.ssh('pwd') == {'host1': '/root', 'host2': '/root'}
    # Check expected processes are running in it
    assert {'ps', 'sshd', 'supervisord', 'beam.smp', 'inet_gethost', 'su', 'apache2',
            'epmd', 'rabbitmq-server', 'sh', 'redis-server', 'postgres'}.\
        issubset(set(extract_column(platform.ssh('ps -A', 'host1'), -1, 1)))
    assert {'ps', 'sshd', 'supervisord', 'apache2'}.\
        issubset(set(extract_column(platform.ssh('ps -A', 'host2'), -1, 1)))
    # check scp file transfer
    platform.ssh('mkdir /root/testdir')
    platform.put(os.path.join(ROOTDIR, 'dummy.txt'), '/root/testdir')
    assert platform.ssh('cat /root/testdir/dummy.txt') == {'host1': 'hello world', 'host2': 'hello world'}
    platform.ssh('rm -rf /root/testdir')


def test_krakens(platform):
    platform, fabric = platform

    # ---- tests
    # check that krakens are running
    assert set(extract_column(platform.ssh('ps aux | grep kraken | grep -v grep', host='host1'), -1)) ==\
           {'/srv/kraken/us-wa/kraken', '/srv/kraken/fr-nw/kraken', '/srv/kraken/fr-npdc/kraken'}
    assert set(extract_column(platform.ssh('ps aux | grep kraken | grep -v grep', host='host2'), -1)) ==\
           {'/srv/kraken/fr-ne-amiens/kraken', '/srv/kraken/fr-idf/kraken', '/srv/kraken/fr-cen/kraken'}

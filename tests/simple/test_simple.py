# encoding: utf-8

import os.path
import time

from fabric import api

from ...docker import get_container_ip
from ...utils import extract_column

ROOTDIR = os.path.dirname(os.path.abspath(__file__))


def test_container(platform):
    platform, fabric = platform
    distri = platform.images.values()[0]

    # ---- tests
    # check platform instantiation in fabric
    assert api.env.name == 'simple'
    assert api.env.roledefs['tyr'] == ['root@' + get_container_ip('{}_simple_host'.format(distri))]
    # Check there's a Debian8 ready image
    assert platform.get_real_images() == [distri]
    # Check there is a platform container running
    assert platform.get_real_containers() == ['{}_simple_host'.format(distri)]
    # Check I can ssh to it
    assert platform.ssh('pwd') == {'host': '/root'}
    # Check expected processes are running in it
    assert {'ps', 'sshd', 'supervisord', 'beam.smp', 'inet_gethost', 'su', 'apache2',
            'epmd', 'rabbitmq-server', 'sh', 'redis-server', 'postgres'}.\
        issubset(set(extract_column(platform.ssh('ps -A', 'host'), -1, 1)))
    # check scp file transfer
    platform.ssh('mkdir /root/testdir')
    platform.put(os.path.join(ROOTDIR, 'dummy.txt'), '/root/testdir')
    assert platform.ssh('cat /root/testdir/dummy.txt', 'host') == 'hello world'
    platform.ssh('rm -rf /root/testdir')


def test_stop_start_kraken(platform):
    platform, fabric = platform

    # ---- tests
    # check that kraken is running
    assert extract_column(platform.ssh('ps aux | grep kraken | grep -v grep', host='host'), -1) ==\
           ['/srv/kraken/default/kraken']
    # stop kraken and check it
    fabric.execute('stop_kraken', 'default')
    time.sleep(1)
    assert platform.ssh('ps aux | grep kraken | grep -v grep', host='host') == ''
    fabric.execute('component.kraken.restart_kraken', 'default', test=False)
    time.sleep(1)
    assert extract_column(platform.ssh('ps aux | grep kraken | grep -v grep', host='host'), -1) ==\
           ['/srv/kraken/default/kraken']

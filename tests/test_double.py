# encoding: utf-8

import os.path

from fabric import api

from ..docker import PlatformManager, ROOTDIR, get_container_ip
from ..fabric_integration import FabricManager
from ..utils import extract_column


def test_simple():
    # ---- setup
    # Create a platform with associated fabric manager
    platform = PlatformManager('double', {'host1': 'debian8', 'host2': 'debian8light'})
    fabric = FabricManager(platform)

    # build a debian8 image ready for Navitia2
    platform.build_images()
    # then run it
    platform.run_containers()

    # ---- tests
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
    # check platform instantiation in fabric
    assert fabric.set_platform() is fabric
    # assert api.env.name == 'double'
    assert api.env.roledefs['eng'] == ['root@' + get_container_ip('debian8_double_host1'),
                                       'root@' + get_container_ip('debian8light_double_host2')]
    # check scp file transfer
    platform.ssh('mkdir /root/testdir')
    platform.put(os.path.join(ROOTDIR, 'tests', 'dummy.txt'), '/root/testdir')
    assert platform.ssh('cat /root/testdir/dummy.txt') == {'host1': 'hello world', 'host2': 'hello world'}
    platform.ssh('rm -rf /root/testdir')

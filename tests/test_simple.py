# encoding: utf-8

import os.path

from fabric import api

from ..docker import PlatformManager, ROOTDIR, get_container_ip
from ..fabric_integration import FabricManager
from ..utils import extract_column


def test_simple_image():
    # ---- setup
    # Create a platform with associated fabric manager
    platform = PlatformManager('simple', {'host': 'debian8'})
    fabric = FabricManager(platform)

    # build a debian8 image ready for Navitia2
    platform.build_images()
    # then run it
    platform.run_containers()

    # ---- tests
    # Check there's a Debian8 ready image
    assert platform.get_real_images() == ['debian8']
    # Check there is a platform container running
    assert platform.get_real_containers() == ['debian8_simple_host']
    # Check I can ssh to it
    assert platform.ssh('pwd') == {'host': '/root'}
    # Check expected processes are running in it
    assert {'ps', 'sshd', 'supervisord', 'beam.smp', 'inet_gethost', 'su', 'apache2',
            'epmd', 'rabbitmq-server', 'sh', 'redis-server', 'postgres'}.\
        issubset(set(extract_column(platform.ssh('ps -A', 'host'), -1, 1)))
    # check platform instantiation in fabric
    assert fabric.set_platform() is fabric
    assert api.env.name == 'simple'
    assert api.env.roledefs['tyr'] == ['root@' + get_container_ip('debian8_simple_host')]
    # check scp file transfer
    platform.ssh('mkdir /root/testdir')
    platform.put(os.path.join(ROOTDIR, 'tests', 'dummy.txt'), '/root/testdir')
    assert platform.ssh('cat /root/testdir/dummy.txt', 'host') == 'hello world'
    platform.ssh('rm -rf /root/testdir')

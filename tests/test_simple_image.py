# encoding: utf-8

from ..docker import PlatformManager
from ..fabric_integration import FabricManager
from ..utils import extract_column


def test_simple_image():
    # Create a platform with associated fabric manager
    platform = PlatformManager('simple', {'host': 'debian8'})
    FabricManager(platform)

    # build a debian8 image ready for Navitia2
    platform.build_images()
    # then run it
    platform.run_containers()

    # Check there's a Debian8 ready image
    assert platform.get_real_images() == ['debian8']
    # Check there is a platform container running
    assert platform.get_real_containers() == ['debian8_simple_host']
    # Check I can ssh to it
    assert platform.ssh('pwd') == {'host': '/root'}
    # Check expected processes are running in it
    assert set(extract_column(platform.ssh('ps -A', 'host'), -1, 1)) ==\
           {'ps', 'sshd', 'supervisord', 'beam.smp', 'inet_gethost', 'su', 'apache2',
            'epmd', 'rabbitmq-server', 'sh', 'redis-server', 'postgres'}

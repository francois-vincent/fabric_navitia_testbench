# encoding: utf-8

import pytest
import time

from ...docker import PlatformManager
from ...fabric_integration import FabricManager


@pytest.fixture(scope='session')
def platform():
    # ---- setup
    # Create a platform with associated fabric manager
    platform = PlatformManager('double', {'host1': 'debian8', 'host2': 'debian8light'})
    fabric = FabricManager(platform)

    # build a debian8 image ready for Navitia2, then run it
    platform.setup()
    time.sleep(1)
    # then set up the fabric platform
    fabric.set_platform()
    # then deploy Navitia on it
    fabric.deploy_from_scratch()
    # make sure that krakens are started
    fabric.execute('component.kraken.restart_all_krakens', wait=False)
    time.sleep(1)

    return platform, fabric

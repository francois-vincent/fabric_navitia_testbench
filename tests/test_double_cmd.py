# encoding: utf-8

import time

from ..docker import PlatformManager
from ..fabric_integration import FabricManager
from ..utils import extract_column


def test_command():
    # ---- setup
    # Create a platform with associated fabric manager
    platform = PlatformManager('double', {'host1': 'debian8', 'host2': 'debian8light'})
    fabric = FabricManager(platform)

    # build a debian8 image ready for Navitia2, then run it
    platform.setup()
    # then set up the fabric platform
    fabric.set_platform()
    # then deploy Navitia on it
    fabric.execute("deploy_from_scratch")
    # make sure that krakens are started
    fabric.execute('component.kraken.restart_all_krakens', wait=False)
    time.sleep(2)

    # ---- tests
    # check that krakens are running
    assert set(extract_column(platform.ssh('ps aux | grep kraken | grep -v grep', host='host1'), -1)) ==\
           {'/srv/kraken/us-wa/kraken', '/srv/kraken/fr-nw/kraken', '/srv/kraken/fr-npdc/kraken'}
    assert set(extract_column(platform.ssh('ps aux | grep kraken | grep -v grep', host='host2'), -1)) ==\
           {'/srv/kraken/fr-ne-amiens/kraken', '/srv/kraken/fr-idf/kraken', '/srv/kraken/fr-cen/kraken'}

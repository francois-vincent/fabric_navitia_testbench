# encoding: utf-8

import time

from ..docker import PlatformManager
from ..fabric_integration import FabricManager
from ..utils import extract_column


def test_command():
    # ---- setup
    # Create a platform with associated fabric manager
    platform = PlatformManager('simple', {'host': 'debian8'})
    fabric = FabricManager(platform)

    # build a debian8 image ready for Navitia2, then run it
    platform.setup()
    # then set up the fabric platform
    fabric.set_platform()
    # then deploy Navitia II on it
    # fabric.execute("deploy_from_scratch")

    # ---- tests
    # check that kraken is running
    assert extract_column(platform.ssh('ps aux | grep kraken | grep -v grep', host='host'), -1) == ['/srv/kraken/default/kraken']
    # stop kraken and check it
    fabric.execute('stop_kraken', 'default')
    time.sleep(1)
    assert platform.ssh('ps aux | grep kraken | grep -v grep', host='host') == ''
    fabric.execute('component.kraken.restart_kraken', 'default', test=False)
    time.sleep(3)
    assert extract_column(platform.ssh('ps aux | grep kraken | grep -v grep', host='host'), -1) == ['/srv/kraken/default/kraken']

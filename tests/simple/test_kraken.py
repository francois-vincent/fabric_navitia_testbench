# encoding: utf-8

import time

from fabric import api

from ..common import get_running_krakens


def test_stop_start_single_kraken(platform):
    platform, fabric = platform

    # check that kraken is running
    assert get_running_krakens(platform, 'host') == ['/srv/kraken/default/kraken']
    # stop kraken and check it
    fabric.execute('stop_kraken', 'default')
    time.sleep(1)
    assert get_running_krakens(platform, 'host') == []
    fabric.execute('component.kraken.restart_kraken', 'default', test=False)
    time.sleep(1)
    assert get_running_krakens(platform, 'host') == ['/srv/kraken/default/kraken']


def test_stop_start_all_krakens(platform):
    platform, fabric = platform

    # check that kraken is running
    assert get_running_krakens(platform, 'host') == ['/srv/kraken/default/kraken']
    # stop kraken and check it
    fabric.execute('stop_kraken', 'default')
    time.sleep(1)
    assert get_running_krakens(platform, 'host') == []
    fabric.execute('component.kraken.restart_all_krakens', wait=False)
    time.sleep(1)
    assert get_running_krakens(platform, 'host') == ['/srv/kraken/default/kraken']

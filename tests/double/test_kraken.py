# encoding: utf-8

import time

from fabric import api

from ..common import get_running_krakens


def test_stop_start_single_kraken(platform):
    platform, fabric = platform

    # check that krakens are running
    assert set(get_running_krakens(platform, 'host1')) ==\
           {'/srv/kraken/us-wa/kraken', '/srv/kraken/fr-nw/kraken', '/srv/kraken/fr-npdc/kraken'}
    assert set(get_running_krakens(platform, 'host2')) ==\
           {'/srv/kraken/fr-ne-amiens/kraken', '/srv/kraken/fr-idf/kraken', '/srv/kraken/fr-cen/kraken'}
    # stop 2 krakens and check them
    fabric.execute('stop_kraken', 'us-wa')
    fabric.execute('stop_kraken', 'fr-cen')
    time.sleep(1)
    assert set(get_running_krakens(platform, 'host1')) ==\
           {'/srv/kraken/fr-nw/kraken', '/srv/kraken/fr-npdc/kraken'}
    assert set(get_running_krakens(platform, 'host2')) ==\
           {'/srv/kraken/fr-ne-amiens/kraken', '/srv/kraken/fr-idf/kraken'}
    # restart these krakens and check them
    fabric.execute('component.kraken.restart_kraken', 'us-wa', test=False)
    fabric.execute('component.kraken.restart_kraken', 'fr-cen', test=False)
    time.sleep(1)
    assert set(get_running_krakens(platform, 'host1')) ==\
           {'/srv/kraken/us-wa/kraken', '/srv/kraken/fr-nw/kraken', '/srv/kraken/fr-npdc/kraken'}
    assert set(get_running_krakens(platform, 'host2')) ==\
           {'/srv/kraken/fr-ne-amiens/kraken', '/srv/kraken/fr-idf/kraken', '/srv/kraken/fr-cen/kraken'}


def test_stop_start_all_krakens(platform):
    platform, fabric = platform

    # check that krakens are running
    assert set(get_running_krakens(platform, 'host1')) ==\
           {'/srv/kraken/us-wa/kraken', '/srv/kraken/fr-nw/kraken', '/srv/kraken/fr-npdc/kraken'}
    assert set(get_running_krakens(platform, 'host2')) ==\
           {'/srv/kraken/fr-ne-amiens/kraken', '/srv/kraken/fr-idf/kraken', '/srv/kraken/fr-cen/kraken'}
    # stop 2 krakens and check them
    fabric.execute('stop_kraken', 'us-wa')
    fabric.execute('stop_kraken', 'fr-cen')
    time.sleep(1)
    assert set(get_running_krakens(platform, 'host1')) ==\
           {'/srv/kraken/fr-nw/kraken', '/srv/kraken/fr-npdc/kraken'}
    assert set(get_running_krakens(platform, 'host2')) ==\
           {'/srv/kraken/fr-ne-amiens/kraken', '/srv/kraken/fr-idf/kraken'}
    # restart these krakens and check them
    fabric.execute('component.kraken.restart_all_krakens', wait=False)
    fabric.execute('component.kraken.restart_all_krakens', wait=False)
    time.sleep(1)
    assert set(get_running_krakens(platform, 'host1')) ==\
           {'/srv/kraken/us-wa/kraken', '/srv/kraken/fr-nw/kraken', '/srv/kraken/fr-npdc/kraken'}
    assert set(get_running_krakens(platform, 'host2')) ==\
           {'/srv/kraken/fr-ne-amiens/kraken', '/srv/kraken/fr-idf/kraken', '/srv/kraken/fr-cen/kraken'}


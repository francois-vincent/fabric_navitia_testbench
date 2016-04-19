# encoding: utf-8

import time
import pytest

from fabric import api

from ..common import get_running_krakens, skipifdev


@skipifdev
def test_stop_start_single_kraken(platform):
    platform, fabric = platform
    # make sure that krakens are started
    fabric.execute('component.kraken.restart_all_krakens', wait=False)
    time.sleep(1)

    # check that kraken is running
    assert get_running_krakens(platform, 'host') == ['/srv/kraken/default/kraken']
    # stop kraken and check it
    fabric.execute('stop_kraken', 'default')
    time.sleep(1)
    assert get_running_krakens(platform, 'host') == []
    fabric.execute('component.kraken.restart_kraken', 'default', test=False)
    time.sleep(1)
    assert get_running_krakens(platform, 'host') == ['/srv/kraken/default/kraken']


@skipifdev
def test_stop_start_all_krakens(platform):
    platform, fabric = platform
    # make sure that krakens are started
    fabric.execute('component.kraken.restart_all_krakens', wait=False)
    time.sleep(1)

    # check that kraken is running
    assert get_running_krakens(platform, 'host') == ['/srv/kraken/default/kraken']
    # stop kraken and check it
    fabric.execute('stop_kraken', 'default')
    time.sleep(1)
    assert get_running_krakens(platform, 'host') == []
    fabric.execute('component.kraken.restart_all_krakens', wait=False)
    time.sleep(1)
    assert get_running_krakens(platform, 'host') == ['/srv/kraken/default/kraken']


def test_test_kraken_nowait_nofail(platform, capsys):
    platform, fabric = platform
    # make sure that krakens are started
    fabric.execute('component.kraken.restart_all_krakens', wait=False)
    time.sleep(1)

    # check that kraken is running
    assert get_running_krakens(platform, 'host') == ['/srv/kraken/default/kraken']

    # test monitor-kraken request
    assert fabric.execute('component.kraken.test_kraken', 'default', fail_if_error=False)
    out, err = capsys.readouterr()
    assert 'http://{}:80/monitor-kraken/?instance=default'.format(platform.get_hosts().values()[0]) in out
    assert "OK: instance default has correct values: {u'status': u'running', u'is_realtime_loaded': False, " \
           "u'start_production_date': u'', u'last_load': u'not-a-date-time', u'end_production_date': u'', " \
           "u'loaded': False, u'publication_date': u'', u'last_load_status': True, " \
           "u'is_connected_to_rabbitmq': True}" in out



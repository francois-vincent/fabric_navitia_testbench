# encoding: utf-8

import time
import pytest

from fabric import api

from ..tests.common import get_running_krakens, skipifdev
from ..utils import extract_column, file_exists


def test_kraken_setup(platform):
    platform, fabric = platform
    assert file_exists('/etc/init.d/kraken_default', api.env.host_ip)
    assert file_exists('/etc/jormungandr.d/default.json', api.env.host_ip)
    assert file_exists('/srv/kraken/default/kraken.ini', api.env.host_ip)


@skipifdev
def test_stop_restart_single_kraken(platform):
    platform, fabric = platform
    # make sure that krakens are started
    fabric.execute('require_all_krakens_started')
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
def test_restart_all_krakens(platform):
    platform, fabric = platform
    # make sure that krakens are started
    fabric.execute('require_all_krakens_started')
    time.sleep(1)

    # check that kraken is running
    assert get_running_krakens(platform, 'host') == ['/srv/kraken/default/kraken']
    # stop kraken and check it
    fabric.execute('stop_kraken', 'default')
    time.sleep(1)
    assert get_running_krakens(platform, 'host') == []
    fabric.execute('restart_all_krakens', wait=False)
    time.sleep(1)
    assert get_running_krakens(platform, 'host') == ['/srv/kraken/default/kraken']


@skipifdev
def test_stop_require_start_kraken(platform):
    platform, fabric = platform
    # make sure that krakens are started
    fabric.execute('require_all_krakens_started')
    time.sleep(1)

    # check that kraken is running
    assert get_running_krakens(platform, 'host') == ['/srv/kraken/default/kraken']
    # stop kraken and check it
    fabric.execute('stop_kraken', 'default')
    time.sleep(1)
    assert get_running_krakens(platform, 'host') == []
    fabric.execute('require_kraken_started', 'default')
    time.sleep(1)
    assert get_running_krakens(platform, 'host') == ['/srv/kraken/default/kraken']


@skipifdev
def test_require_all_krakens_started(platform):
    platform, fabric = platform
    # make sure that krakens are started
    fabric.execute('require_all_krakens_started')
    time.sleep(1)

    # check that kraken is running
    assert get_running_krakens(platform, 'host') == ['/srv/kraken/default/kraken']
    # stop kraken and check it
    fabric.execute('stop_kraken', 'default')
    time.sleep(1)
    assert get_running_krakens(platform, 'host') == []
    fabric.execute('require_all_krakens_started')
    time.sleep(1)
    assert get_running_krakens(platform, 'host') == ['/srv/kraken/default/kraken']


# @skipifdev
def test_stop_start_apache(platform):
    platform, fabric = platform
    # make sure that krakens are started
    fabric.execute('require_all_krakens_started')

    assert 'apache2' in extract_column(platform.ssh('ps -A', 'host'), -1, 1)
    platform.ssh('service apache2 stop')
    time.sleep(1)
    assert 'apache2' not in extract_column(platform.ssh('ps -A', 'host'), -1, 1)
    fabric.execute('require_monitor_kraken_started')
    time.sleep(1)
    assert 'apache2' in extract_column(platform.ssh('ps -A', 'host'), -1, 1)


@skipifdev
def test_test_kraken_nowait_nofail(platform, capsys):
    platform, fabric = platform
    # make sure that krakens are started
    fabric.execute('require_all_krakens_started')
    time.sleep(1)

    # check that kraken is running
    assert get_running_krakens(platform, 'host') == ['/srv/kraken/default/kraken']

    # test monitor-kraken request
    assert fabric.execute('test_kraken', 'default', fail_if_error=False).values()[0] is False
    out, err = capsys.readouterr()
    assert 'http://{}:80/monitor-kraken/?instance=default'.format(platform.get_hosts().values()[0]) in out
    assert "OK: instance default has correct values: {u'status': u'running', u'is_realtime_loaded': False, " \
           "u'start_production_date': u'', u'last_load': u'not-a-date-time', u'end_production_date': u'', " \
           "u'loaded': False, u'publication_date': u'', u'last_load_status': True, " \
           "u'is_connected_to_rabbitmq': True}" in out


@skipifdev
def test_check_dead_instances(platform, capsys):
    platform, fabric = platform
    # make sure that krakens are started
    fabric.execute('require_all_krakens_started')
    time.sleep(1)

    with pytest.raises(SystemExit):
        fabric.execute('component.kraken.check_dead_instances')
    out, err = capsys.readouterr()
    assert 'http://{}:80/monitor-kraken/?instance=default'.format(platform.get_hosts().values()[0]) in out
    assert 'The threshold of allowed dead instance is exceeded.There are 1 dead instances.' in out

# encoding: utf-8

import time

from fabric import api

from ..common import get_running_krakens, skipifdev


@skipifdev
def test_stop_start_single_kraken(platform):
    platform, fabric = platform
    # make sure that krakens are started
    fabric.execute('require_all_krakens_started')
    time.sleep(1)

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


@skipifdev
def test_require_all_krakens_started(platform):
    platform, fabric = platform
    # make sure that krakens are started
    fabric.execute('require_all_krakens_started')
    time.sleep(1)

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
    fabric.execute('require_all_krakens_started')
    time.sleep(1)
    assert set(get_running_krakens(platform, 'host1')) ==\
           {'/srv/kraken/us-wa/kraken', '/srv/kraken/fr-nw/kraken', '/srv/kraken/fr-npdc/kraken'}
    assert set(get_running_krakens(platform, 'host2')) ==\
           {'/srv/kraken/fr-ne-amiens/kraken', '/srv/kraken/fr-idf/kraken', '/srv/kraken/fr-cen/kraken'}


@skipifdev
def test_stop_restart_all_krakens(platform):
    platform, fabric = platform
    # make sure that krakens are started
    fabric.execute('require_all_krakens_started')
    time.sleep(1)

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
    fabric.execute('restart_all_krakens', wait=False)
    time.sleep(1)
    assert set(get_running_krakens(platform, 'host1')) ==\
           {'/srv/kraken/us-wa/kraken', '/srv/kraken/fr-nw/kraken', '/srv/kraken/fr-npdc/kraken'}
    assert set(get_running_krakens(platform, 'host2')) ==\
           {'/srv/kraken/fr-ne-amiens/kraken', '/srv/kraken/fr-idf/kraken', '/srv/kraken/fr-cen/kraken'}


@skipifdev
def test_test_kraken(platform, capsys):
    platform, fabric = platform
    hosts = platform.get_hosts()
    # make sure that krakens are started
    fabric.execute('require_all_krakens_started')
    time.sleep(1)

    # check that krakens are running
    assert set(get_running_krakens(platform, 'host1')) ==\
           {'/srv/kraken/us-wa/kraken', '/srv/kraken/fr-nw/kraken', '/srv/kraken/fr-npdc/kraken'}
    assert set(get_running_krakens(platform, 'host2')) ==\
           {'/srv/kraken/fr-ne-amiens/kraken', '/srv/kraken/fr-idf/kraken', '/srv/kraken/fr-cen/kraken'}

    # test monitor-kraken request
    assert fabric.execute('component.kraken.test_kraken', 'us-wa', fail_if_error=False).values()[0] is False
    out, err = capsys.readouterr()
    assert 'http://{}:80/monitor-kraken/?instance=us-wa'.format(hosts['host1']) in out
    assert fabric.execute('component.kraken.test_kraken', 'fr-cen', fail_if_error=False).values()[0] is False
    out, err = capsys.readouterr()
    assert 'http://{}:80/monitor-kraken/?instance=fr-cen'.format(hosts['host2']) in out
    assert "OK: instance fr-cen has correct values: {u'status': u'running', u'is_realtime_loaded': False, " \
           "u'start_production_date': u'', u'last_load': u'not-a-date-time', u'end_production_date': u'', " \
           "u'loaded': False, u'publication_date': u'', u'last_load_status': True, " \
           "u'is_connected_to_rabbitmq': True}" in out

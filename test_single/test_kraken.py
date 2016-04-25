# encoding: utf-8

import time
import pytest

from fabric import api

from ..utils import file_exists
from ..test_common import skipifdev
from ..test_common.test_kraken import (_test_stop_restart_kraken,
                                       _test_stop_start_apache,
                                       _test_test_kraken_nowait_nofail
                                       )


def test_kraken_setup(platform):
    platform, fabric = platform
    assert file_exists('/etc/init.d/kraken_default', platform.user, api.env.host_ip)
    assert file_exists('/etc/jormungandr.d/default.json', platform.user, api.env.host_ip)
    assert file_exists('/srv/kraken/default/kraken.ini', platform.user, api.env.host_ip)


nominal_krakens = {'host': {'default'}}
krakens_after_stop = {'host': set()}


# @skipifdev
def test_stop_restart_single_kraken(platform):
    _test_stop_restart_kraken(platform,
                             map_start=nominal_krakens,
                             map_stop=krakens_after_stop,
                             stop_pat=('stop_kraken', ('default',)),
                             start_pat=('component.kraken.restart_kraken', ('default',), dict(test=False))
                             )


# @skipifdev
def test_restart_all_krakens(platform):
    _test_stop_restart_kraken(platform,
                             map_start=nominal_krakens,
                             map_stop=krakens_after_stop,
                             stop_pat=('stop_kraken', ('default',)),
                             start_pat=('restart_all_krakens', (), dict(wait=False))
                             )


# @skipifdev
def test_stop_require_start_kraken(platform):
    _test_stop_restart_kraken(platform,
                             map_start=nominal_krakens,
                             map_stop=krakens_after_stop,
                             stop_pat=('stop_kraken', ('default',)),
                             start_pat=('require_kraken_started', ('default',), {}),
                             )


# @skipifdev
def test_require_all_krakens_started(platform):
    _test_stop_restart_kraken(platform,
                             map_start=nominal_krakens,
                             map_stop=krakens_after_stop,
                             stop_pat=('stop_kraken', ('default',)),
                             start_pat=('require_all_krakens_started', (), {}),
                             )


# @skipifdev
def test_stop_start_apache(platform):
    _test_stop_start_apache(platform, ('host',))


# @skipifdev
def test_test_kraken_nowait_nofail(platform, capsys):
    _test_test_kraken_nowait_nofail(platform, capsys, map={'host': {'default'}}, ret_val=False)


# @skipifdev
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

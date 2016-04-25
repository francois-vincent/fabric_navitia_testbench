# encoding: utf-8

from fabric import api

from ..utils import file_exists
from ..test_common import skipifdev
from ..test_common.test_kraken import (_test_stop_restart_kraken,
                                       _test_stop_start_apache,
                                       _test_test_kraken_nowait_nofail
                                       )


def test_kraken_setup(platform):
    platform, fabric = platform
    for krak in api.env.instances:
        assert file_exists('/etc/init.d/kraken_{}'.format(krak), platform.user, api.env.hosts_kraken)
        assert file_exists('/etc/jormungandr.d/{}.json'.format(krak), platform.user, api.env.hosts_jormun[0])
        assert file_exists('/srv/kraken/{}/kraken.ini'.format(krak), platform.user, api.env.hosts_kraken)


nominal_krakens = {'host1': {'us-wa', 'fr-nw', 'fr-npdc', 'fr-ne-amiens', 'fr-idf', 'fr-cen'},
                   'host2': {'us-wa', 'fr-nw', 'fr-npdc', 'fr-ne-amiens', 'fr-idf', 'fr-cen'}}
krakens_after_stop = {'host1': {'fr-nw', 'fr-npdc', 'fr-idf', 'fr-cen'},
                      'host2': {'fr-nw', 'fr-npdc', 'fr-idf', 'fr-cen'}}


# @skipifdev
def test_stop_restart_single_kraken(platform):
    _test_stop_restart_kraken(platform,
                             map_start=nominal_krakens,
                             map_stop=krakens_after_stop,
                             stop_pat=('stop_kraken', ('us-wa', 'fr-ne-amiens')),
                             start_pat=('component.kraken.restart_kraken', ('us-wa', 'fr-ne-amiens'), dict(test=False))
                             )


# @skipifdev
def test_restart_all_krakens(platform):
    _test_stop_restart_kraken(platform,
                             map_start=nominal_krakens,
                             map_stop=krakens_after_stop,
                             stop_pat=('stop_kraken', ('us-wa', 'fr-ne-amiens')),
                             start_pat=('restart_all_krakens', (), dict(wait=False))
                             )


# @skipifdev
def test_stop_require_start_kraken(platform):
    _test_stop_restart_kraken(platform,
                             map_start=nominal_krakens,
                             map_stop=krakens_after_stop,
                             stop_pat=('stop_kraken', ('us-wa', 'fr-ne-amiens')),
                             start_pat=('require_kraken_started', ('us-wa', 'fr-ne-amiens'), {}),
                             )


# @skipifdev
def test_require_all_krakens_started(platform):
    _test_stop_restart_kraken(platform,
                             map_start=nominal_krakens,
                             map_stop=krakens_after_stop,
                             stop_pat=('stop_kraken', ('us-wa', 'fr-ne-amiens')),
                             start_pat=('require_all_krakens_started', (), {}),
                             )


# @skipifdev
def test_stop_start_apache(platform):
    _test_stop_start_apache(platform, ('host1', 'host2'))


# @skipifdev
def test_test_kraken_nowait_nofail(platform, capsys):
    _test_test_kraken_nowait_nofail(platform, capsys,
                                    map={'host1': {'us-wa'}, 'host2': {'fr-ne-amiens'}}, ret_val=None)

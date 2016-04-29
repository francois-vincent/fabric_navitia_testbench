# encoding: utf-8

import pytest

from ..test_common import skipifdev
from ..test_common.test_kraken import (_test_stop_restart_kraken,
                                       _test_stop_start_apache,
                                       _test_test_kraken_nowait_nofail
                                       )


def test_kraken_setup(duplicated):
    duplicated, fabric = duplicated
    for krak in fabric.env.instances:
        assert duplicated.path_exists('/etc/init.d/kraken_{}'.format(krak))
        assert duplicated.path_exists('/srv/kraken/{}/kraken.ini'.format(krak))
        assert duplicated.path_exists('/etc/jormungandr.d/{}.json'.format(krak), 'host1')
        assert not duplicated.path_exists('/etc/jormungandr.d/{}.json'.format(krak), 'host2')


nominal_krakens = {'host1': {'us-wa', 'fr-nw', 'fr-npdc', 'fr-ne-amiens', 'fr-idf', 'fr-cen'},
                   'host2': {'us-wa', 'fr-nw', 'fr-npdc', 'fr-ne-amiens', 'fr-idf', 'fr-cen'}}
krakens_after_stop = {'host1': {'fr-nw', 'fr-npdc', 'fr-idf', 'fr-cen'},
                      'host2': {'fr-nw', 'fr-npdc', 'fr-idf', 'fr-cen'}}


@skipifdev
def test_stop_restart_single_kraken(duplicated):
    _test_stop_restart_kraken(duplicated,
                             map_start=nominal_krakens,
                             map_stop=krakens_after_stop,
                             stop_pat=('stop_kraken', ('us-wa', 'fr-ne-amiens')),
                             start_pat=('component.kraken.restart_kraken', ('us-wa', 'fr-ne-amiens'), dict(test=False))
                             )


@skipifdev
def test_restart_all_krakens(duplicated):
    _test_stop_restart_kraken(duplicated,
                             map_start=nominal_krakens,
                             map_stop=krakens_after_stop,
                             stop_pat=('stop_kraken', ('us-wa', 'fr-ne-amiens')),
                             start_pat=('restart_all_krakens', (), dict(wait=False))
                             )


@skipifdev
def test_stop_require_start_kraken(duplicated):
    _test_stop_restart_kraken(duplicated,
                             map_start=nominal_krakens,
                             map_stop=krakens_after_stop,
                             stop_pat=('stop_kraken', ('us-wa', 'fr-ne-amiens')),
                             start_pat=('require_kraken_started', ('us-wa', 'fr-ne-amiens'), {}),
                             )


@skipifdev
def test_require_all_krakens_started(duplicated):
    _test_stop_restart_kraken(duplicated,
                             map_start=nominal_krakens,
                             map_stop=krakens_after_stop,
                             stop_pat=('stop_kraken', ('us-wa', 'fr-ne-amiens')),
                             start_pat=('require_all_krakens_started', (), {}),
                             )


@skipifdev
def test_stop_start_apache(duplicated):
    _test_stop_start_apache(duplicated, ('host1', 'host2'))


@skipifdev
def test_test_kraken_nowait_nofail(duplicated, capsys):
    _test_test_kraken_nowait_nofail(duplicated, capsys,
                                    map={'host1': {'us-wa'}, 'host2': {'fr-ne-amiens'}}, ret_val=None)


@skipifdev
def test_get_no_data_instances(duplicated, capsys):
    platform, fabric = duplicated
    fabric.execute('component.kraken.get_no_data_instances')
    out, err = capsys.readouterr()
    for instance in fabric.env.instances:
        assert "NOTICE: no data for {}, append it to exclude list".format(instance) in out
    assert set(fabric.env.excluded_instances) == set(fabric.env.instances)


@skipifdev
def test_test_all_krakens_no_wait(duplicated, capsys):
    platform, fabric = duplicated
    fabric.execute('test_all_krakens')
    out, err = capsys.readouterr()
    for instance in fabric.env.instances:
        assert "WARNING: instance {} has no loaded data".format(instance) in out


@skipifdev
def test_check_dead_instances(duplicated, capsys):
    platform, fabric = duplicated
    with pytest.raises(SystemExit):
        fabric.execute('component.kraken.check_dead_instances')
    out, err = capsys.readouterr()
    assert 'The threshold of allowed dead instances is exceeded: ' \
           'Found 12 dead instances out of 6.' in out

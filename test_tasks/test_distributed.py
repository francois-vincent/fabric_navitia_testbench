# encoding: utf-8

from ..test_common import skipifdev


instances_names = {'us-wa', 'fr-nw', 'fr-npdc', 'fr-ne-amiens', 'fr-idf', 'fr-cen'}


@skipifdev
def test_upgrade_kraken(distributed):
    platform, fabric = distributed

    with fabric.set_call_tracker('-component.kraken.upgrade_engine_packages',
                                 '-component.kraken.upgrade_monitor_kraken_packages',
                                 'component.kraken.restart_kraken_on_host',
                                 'component.kraken.require_monitor_kraken_started') as data:
        fabric.execute_forked(
            'tasks.upgrade_kraken', kraken_wait=False, up_confs=False, supervision=False)

    assert len(data()['upgrade_engine_packages']) == 2
    assert len(data()['upgrade_monitor_kraken_packages']) == 2
    assert len(data()['require_monitor_kraken_started']) == 2
    assert len(data()['restart_kraken_on_host']) == len(instances_names)
    assert set((x[0][0].name for x in data()['restart_kraken_on_host'])) == instances_names

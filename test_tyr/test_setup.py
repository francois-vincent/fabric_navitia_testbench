# encoding: utf-8

from ..test_common import skipifdev


@skipifdev
def test_update_tyr_config_file(distributed_undeployed):
    platform, fabric = distributed_undeployed
    platform.docker_exec("mkdir -p /srv/tyr")
    fabric.execute('update_tyr_config_file')
    assert platform.path_exists('/srv/tyr/settings.py')
    assert platform.path_exists('/srv/tyr/settings.wsgi')

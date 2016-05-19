# encoding: utf-8

from mock import patch, DEFAULT

from ..test_common import skipifdev


@skipifdev
def test_upgrade_all(duplicated):
    platform, fabric = duplicated
    with patch.multiple('fabfile.component.load_balancer', _adc_connection=DEFAULT):
        pass
# encoding: utf-8

from ..docker import PlatformManager
from ..fabric_integration import FabricManager


def test_classes():
    # Create a platform with associated fabric manager
    platform = PlatformManager('navitia', {'h1': 'debian8', 'h2': 'debian8'},
                               (('h1', '--param 0'),))
    FabricManager(platform)

    # Check that platform is well initialized
    assert platform.platform == 'navitia'
    assert platform.images == {'h1': 'debian8', 'h2': 'debian8'}
    assert platform.parameters == {'h1': '--param 0'}
    assert platform.containers == {'h1': 'debian8_navitia_h1', 'h2': 'debian8_navitia_h2'}
    assert set(platform.containers_names) == {'debian8_navitia_h1', 'debian8_navitia_h2'}
    assert platform.images_names == {'debian8'}
    assert set(platform.hosts) == {'h1', 'h2'}

    # check that fabric manager is well initialized
    assert platform.managers['fabric'].platform == platform

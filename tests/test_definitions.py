# encoding: utf-8

from docker_integration import PlatformManager
from fabric_integration import FabricManager


def test_platform_creation():
    platform = PlatformManager('navitia', {'h1': 'debian8', 'h2': 'debian8'}, (('h1', '--param 0'),))
    assert platform.platform == 'navitia'
    assert platform.images == {'h1': 'debian8', 'h2': 'debian8'}
    assert platform.parameters == {'h1': '--param 0'}
    assert platform.containers == {'h1': 'debian8_navitia_h1', 'h2': 'debian8_navitia_h2'}
    assert platform.images_names == {'debian8'}
    assert set(platform.hosts) == {'h1', 'h2'}


def test_fabric_creation():
    platform = PlatformManager('navitia', {'h1': 'debian8', 'h2': 'debian8'}, (('h1', '--param 0'),))
    fab = FabricManager(platform)
    assert fab.platform == platform

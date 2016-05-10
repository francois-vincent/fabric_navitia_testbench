# encoding: utf-8

import pytest

from docker import PlatformManager, DeployedPlatformManager
from fabric_integration import FabricManager


def pytest_addoption(parser):
    parser.addoption('--dev', action='store_true',
                     help="run only non decorated tests (default: run all tests")
    parser.addoption('--distri', action='store', default='debian8',
                     help="select a linux distribution (default debian8)")


# ===================     UNDEPLOYED PLATFORMS FIXTURES     =======================

def setup_platform_undeployed(platform, distri):
    # build an image ready for Navitia2, then run it
    platform.setup('rm_container')
    # then set up the fabric platform
    return platform, FabricManager(platform).set_platform(distrib=distri)


@pytest.yield_fixture(scope='function')
def single_undeployed():
    distri = pytest.config.getoption('--distri')
    platform = PlatformManager('single', {'host': distri})
    platform, fabric = setup_platform_undeployed(platform, distri)
    yield platform, fabric
    platform.reset('rm_container')


@pytest.yield_fixture(scope='function')
def distributed_undeployed():
    distri = pytest.config.getoption('--distri')
    platform = PlatformManager('distributed', {'host1': distri, 'host2': distri})
    platform, fabric = setup_platform_undeployed(platform, distri)
    yield platform, fabric
    platform.reset('rm_container')


@pytest.yield_fixture(scope='function')
def duplicated_undeployed():
    distri = pytest.config.getoption('--distri')
    platform = PlatformManager('duplicated', {'host1': distri, 'host2': distri})
    platform, fabric = setup_platform_undeployed(platform, distri)
    yield platform, fabric
    platform.reset('rm_container')


# ===================     DEPLOYED PLATFORMS FIXTURES     =======================

def setup_platform(platform, distri):
    fabric = FabricManager(platform)
    deployed_platform = DeployedPlatformManager(platform, distri).setup('rm_container')
    return deployed_platform, fabric


@pytest.yield_fixture(scope='function')
def single():
    distri = pytest.config.getoption('--distri')
    platform = PlatformManager('single', {'host': distri})
    deployed_platform, fabric = setup_platform(platform, distri)
    yield deployed_platform, fabric
    deployed_platform.reset('rm_container')


@pytest.yield_fixture(scope='function')
def distributed():
    distri = pytest.config.getoption('--distri')
    platform = PlatformManager('distributed', {'host1': distri, 'host2': distri})
    deployed_platform, fabric = setup_platform(platform, distri)
    yield deployed_platform, fabric
    deployed_platform.reset('rm_container')


@pytest.yield_fixture(scope='function')
def duplicated():
    distri = pytest.config.getoption('--distri')
    platform = PlatformManager('duplicated', {'host1': distri, 'host2': distri})
    deployed_platform, fabric = setup_platform(platform, distri)
    yield deployed_platform, fabric
    deployed_platform.reset('rm_container')


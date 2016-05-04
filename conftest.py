# encoding: utf-8

import pytest
import time

from docker import PlatformManager
from fabric_integration import FabricManager


def pytest_addoption(parser):
    parser.addoption('--dev', action='store_true',
                     help="run only non decorated tests (default: run all tests")
    parser.addoption('--reset', action='store_true',
                     help="force reset container, ie force a full navitia redeploy "
                          "(default: reuse existing container")
    parser.addoption('--distri', action='store', default='debian8',
                     help="select a linux distribution (default debian8)")


def setup_platform(platform, distri, deploy=True):
    fabric = FabricManager(platform)
    # build an image ready for Navitia2, then run it
    reset = pytest.config.getoption('--reset')
    platform.setup(reset and 'rm_container')
    time.sleep(1)
    # then set up the fabric platform
    fabric.set_platform(distrib=distri)
    if deploy:
        # then deploy Navitia on it
        fabric.deploy_from_scratch(reset)
    return platform, fabric


@pytest.fixture(scope='module')
def single():
    # Create a platform with associated fabric manager
    distri = pytest.config.getoption('--distri')
    platform = PlatformManager('single', {'host': distri})
    return setup_platform(platform, distri)


@pytest.fixture(scope='module')
def distributed():
    # Create a platform with associated fabric manager
    distri = pytest.config.getoption('--distri')
    platform = PlatformManager('distributed', {'host1': distri, 'host2': distri})
    return setup_platform(platform, distri)


@pytest.fixture(scope='module')
def duplicated():
    # Create a platform with associated fabric manager
    distri = pytest.config.getoption('--distri')
    platform = PlatformManager('duplicated', {'host1': distri, 'host2': distri})
    return setup_platform(platform, distri)


@pytest.fixture(scope='module')
def single_undeployed():
    # Create a platform with associated fabric manager
    distri = pytest.config.getoption('--distri')
    platform = PlatformManager('single', {'host': distri})
    return setup_platform(platform, distri, deploy=False)


@pytest.fixture(scope='module')
def distributed_undeployed():
    # Create a platform with associated fabric manager
    distri = pytest.config.getoption('--distri')
    platform = PlatformManager('distributed', {'host1': distri, 'host2': distri})
    return setup_platform(platform, distri, deploy=False)


@pytest.fixture(scope='module')
def duplicated_undeployed():
    # Create a platform with associated fabric manager
    distri = pytest.config.getoption('--distri')
    platform = PlatformManager('duplicated', {'host1': distri, 'host2': distri})
    return setup_platform(platform, distri, deploy=False)

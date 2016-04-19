# encoding: utf-8

import pytest
import time

from ...docker import PlatformManager
from ...fabric_integration import FabricManager


def pytest_addoption(parser):
    parser.addoption('--reset', action='store_true',
                     help="force reset images and containers (default: reuse existing images and containers")
    parser.addoption('--dev', action='store_true',
                     help="run only non decorated tests (default: run all tests")


@pytest.fixture(scope='session')
def platform():
    # ---- setup
    # Create a platform with associated fabric manager
    platform = PlatformManager('double', {'host1': 'debian8', 'host2': 'debian8light'})
    fabric = FabricManager(platform)

    # build a debian8 image ready for Navitia2, then run it
    platform.setup(pytest.config.getoption('--reset') and 'rm_container')
    time.sleep(1)
    # then set up the fabric platform
    fabric.set_platform()
    # then deploy Navitia on it
    fabric.deploy_from_scratch()

    return platform, fabric
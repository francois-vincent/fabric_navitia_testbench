# encoding: utf-8

import pytest
import time

from ..docker import PlatformManager
from ..fabric_integration import FabricManager


def pytest_addoption(parser):
    parser.addoption('--dev', action='store_true',
                     help="run only non decorated tests (default: run all tests")
    parser.addoption('--reset', action='store_true',
                     help="force reset containers, ie force a full navitia redeploy "
                          "(default: reuse existing containers")
    parser.addoption('--distri', action='store', default='debian8',
                     help="select a linux distribution (default debian8)")


@pytest.fixture(scope='module')
def platform():
    # ---- setup
    # Create a platform with associated fabric manager
    distri = pytest.config.getoption('--distri')
    platform = PlatformManager('duplicated', {'host1': distri, 'host2': '{}light'.format(distri)})
    fabric = FabricManager(platform)

    # build a debian8 image ready for Navitia2, then run it
    reset = pytest.config.getoption('--reset')
    platform.setup(reset and 'rm_container')
    time.sleep(1)
    # then set up the fabric platform
    fabric.set_platform()
    # then deploy Navitia on it
    fabric.deploy_from_scratch(reset)

    return platform, fabric

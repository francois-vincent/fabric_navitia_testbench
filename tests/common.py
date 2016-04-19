# encoding: utf-8

import pytest

from ..utils import extract_column


def get_running_krakens(platform, host):
    return extract_column(platform.ssh('ps aux | grep kraken | grep -v grep', host=host), -1)

skipifdev = pytest.mark.skipif(pytest.config.getoption('--dev'), reason='test skipped with --dev option')

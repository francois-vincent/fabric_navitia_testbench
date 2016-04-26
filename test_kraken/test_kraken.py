# encoding: utf-8

from fabric import api

from ..utils import filter_column, extract_column
from ..test_common import skipifdev


@skipifdev
def test_setup_kraken(double_undeployed):
    platform, fabric = double_undeployed
    fabric.execute('setup_kraken')
    # check that user www-data exists
    assert filter_column(platform.get_data('/etc/passwd', 'host1'), 0, startswith='www-data')
    assert filter_column(platform.get_data('/etc/passwd', 'host2'), 0, startswith='www-data')
    # test existence of paths
    assert platform.path_exists('/srv/kraken')
    assert platform.path_exists('/srv/monitor')
    assert platform.path_exists('/var/log/kraken')
    # test that path belongs to www-data
    assert filter_column(platform.docker_exec('ls -ld /srv/kraken', 'host1'), 2, eq='www-data')
    assert filter_column(platform.docker_exec('ls -ld /srv/kraken', 'host2'), 2, eq='www-data')
    # check existence of monitor configuration
    assert platform.path_exists('/srv/monitor/monitor.wsgi')
    assert platform.path_exists('/srv/monitor/settings.py')
    # check apache configuration for monitor-kraken
    if api.env.distrib == 'debian7':
        assert platform.path_exists('/etc/apache2/conf.d/monitor-kraken')
    else:
        assert platform.path_exists('/etc/apache2/conf-available/monitor-kraken.conf')
    # check that apache is started
    assert 'apache2' in extract_column(platform.docker_exec('ps -A', 'host1'), -1, 1)
    assert 'apache2' in extract_column(platform.docker_exec('ps -A', 'host2'), -1, 1)


# @skipifdev
def test_upgrade_engine_packages(double_undeployed):
    platform, fabric = double_undeployed
    # fabric.execute('upgrade_engine_packages')
    # platform.docker_exec('apt-get update')
    # assert platform.get_version('python2.7', 'host1').startswith('2.7')
    # assert platform.get_version('python2.7', 'host2').startswith('2.7')
    if api.env.distrib == 'debian7':
        assert platform.get_version('libzmq-dev', 'host1')
        assert platform.get_version('libzmq-dev', 'host2')
    else:
        assert platform.get_version('libzmq3-dev', 'host1')
        assert platform.get_version('libzmq3-dev', 'host2')
    assert platform.get_version('navitia-kraken', 'host1')
    assert platform.get_version('navitia-kraken', 'host2')

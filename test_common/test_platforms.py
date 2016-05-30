# encoding: utf-8

from collections import defaultdict

from fabric.api import env

from fabfile.env.platforms import use

from . import skipifdev


class Counter(defaultdict):
    def __init__(self, instances):
        defaultdict.__init__(self, list)
        for k, v in instances.iteritems():
            self[v.kraken_zmq_socket.rsplit(':', 1)[1]].append(k)

    def check(self):
        for k, v in self.iteritems():
            assert len(v) == 1, 'zmq_socket_port {}: hosts {}'.format(k, v)


# @skipifdev
def test_prod_setup():
    env.instances = {}
    use('prod')
    assert len(env.instances) == 67
    assert env.use_zmq_socket_file is False
    Counter(env.instances).check()
    assert env.instances['sandbox'].zmq_server == env.zmq_server
    assert env.instances['sandbox'].kraken_engines == env.eng_hosts[:2]
    assert env.instances['ar'].zmq_server == env.zmq_server
    assert env.instances['ar'].kraken_engines == env.eng_hosts[2:]


# @skipifdev
def test_pre_setup():
    env.instances = {}
    use('pre')
    assert len(env.instances) == 67
    assert env.use_zmq_socket_file is False
    Counter(env.instances).check()
    assert env.instances['sandbox'].zmq_server == env.zmq_server
    assert env.instances['sandbox'].kraken_engines == env.roledefs['eng'][1:]
    assert env.instances['fr-nor'].zmq_server == env.zmq_server
    assert env.instances['fr-nor'].kraken_engines == env.roledefs['eng'][:1]


# @skipifdev
def test_sim_setup():
    env.instances = {}
    use('sim')
    assert len(env.instances) == 45
    assert env.use_zmq_socket_file is False
    Counter(env.instances).check()
    assert env.instances['sandbox'].zmq_server == env.zmq_server
    assert env.instances['sandbox'].kraken_engines == env.roledefs['eng']


# @skipifdev
def test_internal_setup():
    env.instances = {}
    use('internal')
    assert len(env.instances) == 25
    assert env.use_zmq_socket_file is False
    Counter(env.instances).check()
    assert env.instances['fr-nor'].zmq_server == env.zmq_server
    assert env.instances['fr-nor'].kraken_engines == env.roledefs['eng']


# @skipifdev
def test_customer_setup():
    env.instances = {}
    use('customer')
    assert len(env.instances) == 25
    assert env.use_zmq_socket_file is False
    Counter(env.instances).check()
    assert env.instances['fr-nor'].zmq_server == env.zmq_server
    assert env.instances['fr-nor'].kraken_engines == env.roledefs['eng']

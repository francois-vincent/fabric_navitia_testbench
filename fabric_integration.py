# encoding: utf-8

from importlib import import_module
import sys

import docker_wrapper

fabric_navitia_path = None
for x in sys.path:
    if 'fabric_navitia' in x and 'fabric_navitia' == x.split('/')[-1]:
        fabric_navitia_path = x
        break
if not fabric_navitia_path:
    raise RuntimeError("Could not find module 'fabric_navitia', please set PYTHONPATH accordingly")

from fabric import api, operations, context_managers, tasks

import fabfile


with docker_wrapper.cd(fabric_navitia_path):
    fabric_tasks = docker_wrapper.Command('fab toto').stdout_column(0, 2)


def get_fabric_task(task):
    fab_task = []
    for x in fabric_tasks:
        if task == x:
            return task
        if task in x and x.split('.')[-1] in task:
            fab_task.append(x)
    if not fab_task:
        raise RuntimeError("Fabric task not found: {}".format(task))
    elif len(fab_task) > 1:
        raise RuntimeError("Multiple Fabric tasks found for {}: {}, "
                           "please be more specific".format(task, fab_task))
    return fab_task[0]


class FabricManager(object):
    """
    class in charge of running fabric_navitia tasks on a running platform
    """
    def __init__(self, platform):
        self.platform = platform

    def get_hosts(self, raises=False):
        self.hosts = {k: docker_wrapper.get_container_ip(v) for k, v in self.platform.containers.iteritems()}
        if raises:
            found, expected = len(self.hosts), len(self.platform.containers)
            if found < expected:
                raise RuntimeError("Expecting {} running containers, found {}".format(expected, found))
        return self.hosts

    def set_platform(self):
        module = import_module('platforms.' + self.platform.platform)
        getattr(module, self.platform.platform)(**self.get_hosts(True))
        return self

    def execute(self, cmd, *args):
        fab_task = get_fabric_task(cmd)
        if '.' in fab_task:
            module, task = fab_task.rsplit('.', 1)
            module = import_module('fabfile.' + module)
            cmd = getattr(module, task)
        else:
            module = import_module('fabfile')
            cmd = getattr(module, fab_task)
        api.execute(cmd, *args)
        return self

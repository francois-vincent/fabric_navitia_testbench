# encoding: utf-8

from importlib import import_module
import sys

import utils

fabric_navitia_path = None
for x in sys.path:
    if 'fabric_navitia' in x and 'fabric_navitia' == [y for y in x.split('/') if y][-1]:
        fabric_navitia_path = x
        break
if not fabric_navitia_path:
    raise RuntimeError("Could not find module 'fabric_navitia', please set PYTHONPATH accordingly")

from fabric import api


with utils.cd(fabric_navitia_path):
    fabric_tasks = utils.Command('fab no_such_task').stdout_column(0, 2)


def get_fabric_task(task):
    fab_task = []
    for x in fabric_tasks:
        if x.endswith(task):
            fab_task.append(x)
    if not fab_task:
        raise RuntimeError("Fabric task not found: {}".format(task))
    elif len(fab_task) > 1:
        if len(fab_task) == 2 and task == fab_task[0]:
            return fab_task[1]
        raise RuntimeError("Multiple Fabric tasks found for {}: {}, "
                           "please be more specific".format(task, fab_task))
    return fab_task[0]


def get_task_description(task):
    desc = '{}.{}'.format(task.__module__, task.name)
    if desc.__doc__:
        desc += ' [{}]'.format(task.__doc__.splitlines()[0])
    return desc


class FabricManager(object):
    """
    class in charge of running fabric_navitia tasks on a running platform
    """
    def __init__(self, platform):
        self.platform = platform
        self.platform.register_manager('fabric', self)

    def set_platform(self):
        module = import_module('.platforms.' + self.platform.platform, 'fabric_navitia_testbench')
        getattr(module, self.platform.platform)(**self.platform.get_hosts(True))
        if getattr(api.env, 'default_ssh_user'):
            self.platform.user = api.env.default_ssh_user
        return self

    def execute(self, task, *args, **kwargs):
        fab_task = get_fabric_task(task)
        try:
            if '.' in fab_task:
                module, task = fab_task.rsplit('.', 1)
                module = import_module('fabfile.' + module)
                cmd = getattr(module, task)
            else:
                module = import_module('fabfile')
                cmd = getattr(module, fab_task)
        except ImportError as e:
            raise RuntimeError("Can't find task {} in fabfile {}/fabfile: [{}]".format(fab_task, fabric_navitia_path, e))
        print(utils.magenta("Running task " + get_task_description(cmd)))
        api.execute(cmd, *args, **kwargs)
        return self

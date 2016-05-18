# encoding: utf-8

# here are the definitions and class that manage the interactions with the python fabric module
# and fabric_navitia.
# good practice: test modules should only access fabric and fabric_navitia this way


from cStringIO import StringIO
from importlib import import_module
import multiprocessing
import os.path
import Queue
import sys

from fabric import api

import utils

fabric_navitia_path = None
for x in sys.path:
    if 'fabric_navitia' in x and 'fabric_navitia' == [y for y in x.split('/') if y][-1]:
        fabric_navitia_path = x
        break
if not fabric_navitia_path:
    raise RuntimeError("Could not find module 'fabric_navitia', please set PYTHONPATH accordingly")

ROOT = os.path.basename(os.path.dirname(__file__))


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
            return fab_task[0]
        raise RuntimeError("Multiple Fabric tasks found for {}: {}, "
                           "please be more specific".format(task, fab_task))
    return fab_task[0]


def get_task_description(task):
    desc = '{}.{}'.format(task.__module__, task.name)
    if task.__doc__:
        desc += ' [{}]'.format(task.__doc__.splitlines()[0])
    return desc


class ProcessProxy(object):

    def __init__(self, task, *args, **kwargs):
        self.out_q = multiprocessing.Queue()
        self.runner = multiprocessing.Process(target=
                                      lambda: self.out_q.put(self.run(task, *args, **kwargs)))

    def start(self):
        self.runner.start()
        return self

    def run(self, task, *args, **kwargs):
        sys.stdout, sys.stderr = StringIO(), StringIO()
        try:
            return (task(*args, **kwargs), None, sys.stdout.getvalue(), sys.stderr.getvalue())
        except BaseException as e:
            return (None, e, sys.stdout.getvalue(), sys.stderr.getvalue())

    def join(self):
        self.runner.join()
        try:
            return self.out_q.get_nowait()
        except Queue.Empty:
            return (None, None, '', '')
        finally:
            self.out_q.close()


class FabricManager(object):
    """
    Class in charge of running fabric_navitia tasks on a running platform.
    This is the only object you usually have to import in a test file.
    """
    def __init__(self, platform):
        self.api = api
        self.env = api.env
        self.register_platform(platform)

    def register_platform(self, platform):
        self.platform = platform
        self.platform.register_manager('fabric', self)

    @staticmethod
    def get_object(obj_spec):
        try:
            if '.' in obj_spec:
                module, task = obj_spec.rsplit('.', 1)
                module = import_module('fabfile.' + module)
                return getattr(module, task)
            else:
                module = import_module('fabfile')
                return getattr(module, obj_spec)
        except ImportError as e:
            raise RuntimeError("Can't find object {} in fabfile {}/fabfile: [{}]".format(obj_spec, fabric_navitia_path, e))

    def set_platform(self, **write):
        """ Sets fabric.api.env attributes from the selected platform
        The setup follows the sequence:
        fabfile.env.platforms > tests_integration.platforms.common > tests_integration.platforms.<selected_platform>
        :param write: dictionary to inject into fabric.api.env
        """
        module = import_module('.platforms.' + self.platform.platform_name, ROOT)
        getattr(module, self.platform.platform_name)(**self.platform.get_hosts(True))
        self.platform.user = getattr(self.env, 'default_ssh_user', 'root')
        for k, v in write.iteritems():
            setattr(self.env, k, v)
        # wait sshd daemons running on host platform
        self.platform.wait_process('/usr/sbin/sshd')
        return self

    def execute(self, task, *args, **kwargs):
        cmd = self.get_object(get_fabric_task(task))
        print(utils.magenta("Running task " + get_task_description(cmd)))
        return self.api.execute(cmd, *args, **kwargs)

    def execute_forked(self, task, *args, **kwargs):
        """ Execute fabric task in a forked process. This allows fabric to do anything
            it likes, including crashing and resetting the SSH channels to the platform.
        :return: a tuple (value returned by the fabric task or None,
                          exception raised or None,
                          stdout produced during the execution of the task,
                          stderr produced during the execution of the task
                         )
        """
        cmd = self.get_object(get_fabric_task(task))
        print(utils.magenta("Running task (fabric forked) " + get_task_description(cmd)))
        return ProcessProxy(self.api.execute, cmd, *args, **kwargs).start().join()

    def get_version(self, role='eng'):
        return self.execute('utils.get_version', role).values()[0]

    def deploy_from_scratch(self, force=False):
        if force:
            self.execute("deploy_from_scratch")
            return self
        for role in ('tyr', 'eng', 'ws'):
            installed, candidate = self.get_version(role)
            if not installed or installed != candidate:
                self.execute("deploy_from_scratch")
                break
        return self

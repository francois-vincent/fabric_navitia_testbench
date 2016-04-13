# encoding: utf-8

from collections import Mapping
import os

from utils import Command, command, ssh, cd, yellow, red

ROOTDIR = os.path.dirname(os.path.abspath(__file__))


def get_containers(filter=None, all=True):
    """ Get containers names, with optional filter on name.
    :param filter: if string, get containers names containing it, if container, get images in this set.
    :param all: if False, get only running containers, else get all containers.
    :return:
    """
    docker_ps = Command('docker ps -a' if all else 'docker ps').stdout_column(-1, 1)
    if filter:
        if isinstance(filter, basestring):
            return [x for x in docker_ps if filter in x]
        else:
            return [x for x in docker_ps if x in filter]
    return [x for x in docker_ps]


def get_images(filter=None):
    """ Get images names, with optional filter on name.
    :param filter: if string, get images names containing it, if container, get images in this set.
    :return:
    """
    docker_images = Command('docker images').stdout_column(0, 1)
    if filter:
        if isinstance(filter, basestring):
            return [x for x in docker_images if filter in x]
        else:
            return [x for x in docker_images if x in filter]
    return [x for x in docker_images]


def containers_delete(containers):
    for container in get_containers(containers):
        print(yellow("Delete container {}".format(container)))
        return command('docker', 'rm', container)


def containers_stop(containers):
    for container in get_containers(containers, all=False):
        print(yellow("Stop container {}".format(container)))
        return command('docker', 'stop', container)


def images_delete(images):
    for image in get_images(images):
        print(red("Delete image {}".format(image)))
        return command('docker', 'rmi', image)


def docker_build(context, image, tag=None):
    cmd = 'docker build -f {}/Dockerfile{} .'.format(image, ' -t {}'.format(tag) if tag else '')
    print(yellow(cmd))
    with cd(context):
        return Command(cmd).returncode


def docker_run(image, container=None, host=None, parameters=None):
    cmd = 'docker run -d '
    if container:
        cmd += '--name {} '.format(container)
    if host:
        cmd += '-h {} '.format(host)
    if parameters:
        cmd += parameters + ' '
    cmd += image
    print(yellow(cmd))
    return Command(cmd).returncode


def docker_start(container):
    return Command('docker start {}'.format(container)).returncode


def get_container_ip(container):
    return Command("docker inspect --format '{{ .NetworkSettings.IPAddress }}' %s" % container).stdout.strip()


class PlatformManager(object):
    """
    class in charge of bringing up a running platform and performing other docker magic
    Check existence or creates the images,
    then check existence or runs the containers.
    Optionally, stops and commits the containers.
    """
    def __init__(self, platform, images, parameters=()):
        """
        :param platform: string
        :param images: dictionary/pair iterable of container-name:image
        :param parameters: dictionary/pair iterable of container-name:iterable of strings
        """
        self.platform = platform
        self.images = images if isinstance(images, Mapping) else dict(images)
        self.parameters = parameters if isinstance(parameters, Mapping) else dict(parameters)
        self.containers = {k: '_'.join((v, self.platform, k)) for k, v in self.images.iteritems()}
        self.hosts = self.images.keys()
        self.images_names = set(self.images.values())
        self.containers_names = self.containers.values()
        self.managers = {}

    def register_manager(self, name, manager):
        self.managers[name] = manager
        return self

    def get_manager(self, name):
        return self.managers.get(name)

    def get_real_images(self):
        return get_images(self.images_names)

    def get_real_containers(self, all=False):
        return get_containers(self.containers_names, all)

    def setup(self, reset=None):
        """
        1- ensures images are created, otherwise, creates them
        2- ensures containers are created and started otherwise creates and/or starts them
        """
        self.reset(reset)
        self.build_images()
        self.run_containers()
        return self

    def reset(self, reset='all'):
        if reset in ('all', 'containers'):
            self.containers_stop()
            self.containers_delete()
        if reset == 'all':
            self.images_delete()
        return self

    def build_images(self):
        existing = self.get_real_images()
        for image in self.images_names:
            if image not in existing:
                docker_build(os.path.join(ROOTDIR, 'images'), image, image)
        return self

    def run_containers(self):
        running = self.get_real_containers()
        existing = self.get_real_containers(True)
        for k, v in self.images.iteritems():
            container = self.containers[k]
            if container in running:
                continue
            if container in existing:
                docker_start(container)
            else:
                docker_run(v, container, container, self.parameters.get(k))
        return self

    def images_delete(self):
        images_delete(self.images_names)
        return self

    def containers_stop(self):
        containers_stop(get_containers(self.containers.values()))
        return self

    def containers_delete(self):
        containers_delete(get_containers(self.containers.values(), True))
        return self

    def ssh(self, cmd, host=None):
        if host:
            return ssh('root', get_container_ip(self.containers[host]), cmd)
        return {k: ssh('root', get_container_ip(v), cmd) for k, v in self.containers.iteritems()}

    def commit_containers(self):
        """
        commited container have a convention naming: image_platform_container-name
        """
        return self

    def docker_diff(self, reference):
        """
        check docker diff against an external reference
        :param reference: string, a reference text to be checked
        """

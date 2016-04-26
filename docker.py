# encoding: utf-8

from collections import Mapping
import os

import utils

ROOTDIR = os.path.dirname(os.path.abspath(__file__))


def get_containers(filter=None, all=True):
    """ Get containers names, with optional filter on name.
    :param filter: if string, get containers names containing it, if container, get images in this set.
    :param all: if False, get only running containers, else get all containers.
    :return:
    """
    docker_ps = utils.Command('docker ps -a' if all else 'docker ps').stdout_column(-1, 1)
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
    docker_images = utils.Command('docker images').stdout_column(0, 1)
    if filter:
        if isinstance(filter, basestring):
            return [x for x in docker_images if filter in x]
        else:
            return [x for x in docker_images if x in filter]
    return [x for x in docker_images]


def container_delete(container):
    return utils.command('docker rm ' + container)


def container_stop(container):
    return utils.command('docker stop ' + container)


def image_delete(image):
    return utils.command('docker rmi ' + image)


def image_delete_and_containers(image):
    """ WARNING: This will remove an image and all its dependant containers
    """
    for container in utils.extract_column(utils.filter_column(utils.Command('docker ps').stdout, 1, eq=image), -1):
        container_stop(container)
    for container in utils.extract_column(utils.filter_column(utils.Command('docker ps -a').stdout, 1, eq=image), -1):
        container_delete(container)
    return image_delete(image)


def docker_build(context, image, tag=None):
    cmd = 'docker build -f {}/Dockerfile{} .'.format(image, ' -t {}'.format(tag) if tag else '')
    print(utils.yellow(cmd))
    with utils.cd(context):
        return utils.Command(cmd).returncode


def docker_run(image, container=None, host=None, parameters=None):
    cmd = 'docker run -d '
    if container:
        cmd += '--name {} '.format(container)
    if host:
        cmd += '-h {} '.format(host)
    if parameters:
        cmd += parameters + ' '
    cmd += image
    print(utils.yellow(cmd))
    return utils.Command(cmd).returncode


def docker_start(container):
    return utils.Command('docker start {}'.format(container)).returncode


def get_container_ip(container, raises=False):
    cmd = utils.Command("docker inspect --format '{{ .NetworkSettings.IPAddress }}' %s" % container)
    if raises and cmd.stderr:
        raise RuntimeError("Container {} is not running".format(container))
    return cmd.stdout.strip()


def docker_exec(container, cmd, user=None, stdout_only=True, return_code_only=False, raises=False):
    docker_cmd = 'docker exec -it {} {} {}'.format('-u {}'.format(user) if user else '', container, cmd)
    if return_code_only:
        return utils.command(docker_cmd)
    dock = utils.Command(docker_cmd)
    if raises and dock.returncode:
        raise RuntimeError("Error while executing <{}>: [{}]".
                           format(docker_cmd, dock.stderr.strip() or dock.returncode))
    if stdout_only:
        return dock.stdout.strip()
    return dock


def path_exists(path, container):
    return not docker_exec(container, 'test -e {}'.format(path), return_code_only=True)


def put_data(data, dest, container, append=False, user=None, perms=None):
    if append and not path_exists(dest, container):
        docker_exec(container, 'touch {}'.format(dest), user=user)
    cmd = ''.join(('echo "', data, '" >>' if append else '" >', dest))
    docker_exec(container, "/bin/sh -c '{}'".format(cmd), user=user, raises=True)
    if perms:
        utils.command('docker exec {} chmod {} {}'.format(container, perms, dest))


def get_data(source, container):
    return docker_exec(container, 'cat {}'.format(source), raises=True)


def put_file(source, dest, container, user=None, perms=None):
    pass


class PlatformManager(object):
    """
    Class in charge of bringing up a running platform and performing other docker magic
    Check existence or creates the images,
    then check existence or runs the containers.
    Optionally, stops and commits the containers.
    """
    def __init__(self, platform, images, parameters=(), user='root'):
        """
        :param platform: string
        :param images: dictionary/pair iterable of container-name:image
        :param parameters: dictionary/pair iterable of container-name:iterable of strings
        """
        self.images_rootdir = ROOTDIR
        self.platform = platform
        self.user = user
        self.images = images if isinstance(images, Mapping) else dict(images)
        self.parameters = parameters if isinstance(parameters, Mapping) else dict(parameters)
        self.containers = {k: '-'.join((v, self.platform, k)) for k, v in self.images.iteritems()}
        self.hosts = self.images.keys()
        self.images_names = set(self.images.values())
        self.containers_names = self.containers.values()
        self.managers = {}

    def register_manager(self, name, manager):
        self.managers[name] = manager
        return self

    def get_manager(self, name):
        return self.managers.get(name)

    def setup(self, reset=None):
        """
        1- ensures images are created, otherwise, creates them
        2- ensures containers are created and started otherwise creates and/or starts them
        """
        self.reset(reset)
        self.build_images()
        self.run_containers()
        return self

    def reset(self, reset='rm_image'):
        if reset == 'uproot':
            self.images_delete(uproot=True)
        if reset in ('stop', 'rm_container', 'rm_image'):
            self.containers_stop()
        if reset in ('rm_container', 'rm_image'):
            self.containers_delete()
        if reset == 'rm_image':
            self.images_delete()
        return self

    def build_images(self, reset=None):
        self.reset(reset)
        existing = self.get_real_images()
        for image in self.images_names:
            if image not in existing:
                print(utils.yellow("Build image {}".format(image)))
                docker_build(os.path.join(self.images_rootdir, 'images'), image, image)
        return self

    def run_containers(self, reset=None):
        if reset == 'rm_image':
            raise RuntimeError("Can't remove images before running containers")
        self.reset(reset)
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

    def get_real_images(self):
        return get_images(self.images_names)

    def get_real_containers(self, all=False):
        return get_containers(self.containers_names, all)

    def images_delete(self, uproot=False):
        func = image_delete_and_containers if uproot else image_delete
        for image in self.get_real_images():
            print(utils.red("Delete image {}".format(image)))
            func(image)
        return self

    def containers_stop(self):
        for container in self.get_real_containers():
            print(utils.yellow("Stop container {}".format(container)))
            container_stop(container)
        return self

    def containers_delete(self):
        for container in self.get_real_containers(True):
            print(utils.yellow("Delete container {}".format(container)))
            container_delete(container)
        return self

    def get_hosts(self, raises=False):
        """ Returns the dict(host, ip) of containers actually running, or raises
           an exception if the number of running containers differs from the number
           of defined containers.
        """
        self.hosts = {k: get_container_ip(v) for k, v in self.containers.iteritems()}
        if raises:
            expected = len(self.containers)
            found = len([x for x in self.hosts.itervalues() if x])
            if found < expected:
                raise RuntimeError("Expecting {} running containers, found {}".format(expected, found))
        return self.hosts

    def ssh(self, cmd, host=None):
        """ this method requires that an ssh daemon is running on the target
            and that an authorized_keys file is set with a rsa plubilc key,
            all conditions met by images provided in this project.
        """
        if host:
            return utils.ssh(self.user, get_container_ip(self.containers[host]), cmd)
        return {k: utils.ssh(self.user, get_container_ip(v), cmd) for k, v in self.containers.iteritems()}
    
    def scp(self, source, dest, host=None):
        """ this method requires that an ssh daemon is running on the target
            and that an authorized_keys file is set with a rsa plubilc key,
            all conditions met by images provided in this project.
        """
        containers = [self.containers[host]] if host else self.containers.itervalues()
        for container in containers:
            utils.scp(source, dest, get_container_ip(container), self.user)
        return self

    def ssh_put_data(self, data, dest, host=None, append=False):
        if not append:
            self.ssh('touch {}'.format(dest), host)
        cmd = ''.join(('echo "', data, '" >>' if append else '" >', dest))
        self.ssh(cmd, host)
        return self

    def ssh_get_data(self, source, host=None):
        return self.ssh('cat {}'.format(source), host)

    def docker_exec(self, cmd, host=None):
        if host:
            return docker_exec(self.containers[host], cmd)
        return {k: docker_exec(v, cmd) for k, v in self.containers.iteritems()}

    def put_data(self, data, dest, host=None, append=False):
        containers = [self.containers[host]] if host else self.containers.itervalues()
        for container in containers:
            put_data(data, dest, container, append=append)
        return self

    def put_file(self, data, dest, host=None, append=False):
        containers = [self.containers[host]] if host else self.containers.itervalues()
        for container in containers:
            put_data(data, dest, container, append=append)
        return self

    def get_data(self, source, host=None):
        if host:
            return get_data(source, self.containers[host])
        return {k: get_data(source, v) for k, v in self.containers.iteritems()}

    def path_exists(self, path, host=None):
        containers = [self.containers[host]] if host else self.containers.itervalues()
        for container in containers:
            if not path_exists(path, container):
                return False
        return True

    def commit_containers(self):
        """
        commited container have a convention naming: image_platform_container-name
        """
        return self

    def docker_diff(self):
        """
        get docker diff
        """
        # TODO this could only be useful if krakens could start automatically...

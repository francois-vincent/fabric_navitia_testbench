# encoding: utf-8

from utils import Command, command, cd


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
        print("Delete container {}".format(container))
        return command('docker', 'rm', container)


def containers_stop(containers):
    for container in get_containers(containers, all=False):
        print("Stop container {}".format(container))
        return command('docker', 'stop', container)


def images_delete(images):
    for image in get_images(images):
        print("Delete image {}".format(image))
        return command('docker', 'rmi', image)


def docker_build(context, image, tag=None):
    cmd = 'docker build -f {}/Dockerfile{} .'.format(image, ' -t {}'.format(tag) if tag else '')
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
    return Command(cmd).returncode


def docker_start(container):
    return Command('docker start {}'.format(container)).returncode


def get_container_ip(container):
    return Command("docker inspect --format '{{ .NetworkSettings.IPAddress }}' %s" % container).stdout.strip()
